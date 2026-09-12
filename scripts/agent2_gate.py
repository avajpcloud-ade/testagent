#!/usr/bin/env python3
"""Agent2 deterministic gate.

Recomputes the verdict from the artifacts themselves, so neither an agent nor a
reviewer has to trust an LLM's "done".

Usage:
    python scripts/agent2_gate.py <project> [--phase spec|infra]

Exit codes:
    0  PASS
    1  BLOCKED  — unresolved fields; 差戻し to the design team
    2  BROKEN   — artifacts missing, stale, invalid, or inconsistent
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESOLVED = {"confirmed", "answered"}
# Wordings that mean "not decided yet". A field is only genuinely `missing` if the
# design says nothing, or says one of these.
GAP_MARKERS = re.compile(r"未定|未確定|別途決定|別途指定|要確認|検討中|TBD|N/?A", re.IGNORECASE)
SCOPES = {"resourceGroup", "subscription"}
TRACE_COLUMNS = ["field_path", "value", "status", "source_ids", "source_locations", "bicep_ref"]
ARTIFACTS = {
    "extracted-parameters.json": "extracted-parameters.schema.json",
    "deployment-spec.generated.json": "deployment-spec.schema.json",
    "normalized.json": "normalized.schema.json",
}

try:
    from jsonschema import Draft202012Validator
except ImportError:  # CI installs it; locally we fall back to the structural checks below
    Draft202012Validator = None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def schema_errors(doc: dict, schema_file: str) -> list[str]:
    if Draft202012Validator is None:
        return []
    schema = json.loads((ROOT / "schemas" / schema_file).read_text(encoding="utf-8"))
    out = []
    for e in Draft202012Validator(schema).iter_errors(doc):
        where = "/".join(map(str, e.absolute_path)) or "(root)"
        out.append(f"{schema_file}: {where}: {e.message}")
    return out


def iter_fields(doc: dict):
    """Yield (field_path, field) in the path format used by issue-report.md and traceability.csv."""
    for key, field in doc["target"].items():
        yield f"target:{key}", field
    for key, field in (doc.get("tags") or {}).items():
        yield f"tags:{key}", field
    for res in doc["resources"]:
        for key, field in res["settings"].items():
            yield f"{res['id']}:{key}", field


def check(project: str, phase: str):
    errors: list[str] = []
    blocking: list[str] = []
    notes: list[str] = []
    design, work, infra = ROOT / "design" / project, ROOT / "work" / project, ROOT / "infra" / project

    if Draft202012Validator is None:
        notes.append("jsonschema not installed — schema validation skipped (pip install jsonschema)")

    # ---- 1. artifacts exist, parse, and match their schemas -------------------
    docs = {}
    for name, schema in ARTIFACTS.items():
        path = work / name
        if not path.exists():
            errors.append(f"missing artifact: {rel(path)}")
            continue
        try:
            docs[name] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{name}: invalid JSON: {e}")
            continue
        errors += schema_errors(docs[name], schema)
    for name in ("issue-report.md", "traceability.csv"):
        if not (work / name).exists():
            errors.append(f"missing artifact: {rel(work / name)}")
    if errors:
        return errors, blocking, notes

    ext = docs["extracted-parameters.json"]
    spec = docs["deployment-spec.generated.json"]
    norm = docs["normalized.json"]

    try:
        # ---- 2. sources are fresh -------------------------------------------
        listed = set()
        for d in ext["sourceDocuments"]:
            p = ROOT / d["path"]
            listed.add(p.resolve())
            if not p.exists():
                errors.append(f"source no longer exists: {d['path']}")
            elif sha256(p) != d["sha256"]:
                errors.append(f"source changed since extraction — re-run agent2-extract: {d['path']}")
        design_doc = design / "detailed-design.md"
        if not design_doc.exists():
            errors.append(f"required input missing: {rel(design_doc)}")
        for p in (design_doc, design / "answers.md"):
            if p.exists() and p.resolve() not in listed:
                errors.append(f"{rel(p)} exists but was not used in extraction — re-run agent2-extract")

        # ---- 3. IDs and cross-artifact consistency --------------------------
        params = {p["id"]: p for p in ext["parameters"]}
        if len(params) != len(ext["parameters"]):
            errors.append("duplicate parameter IDs in extracted-parameters.json")

        spec_res = {r["id"]: r for r in spec["resources"]}
        norm_res = {r["id"]: r for r in norm["resources"]}
        if len(norm_res) != len(norm["resources"]):
            errors.append("duplicate resource IDs in normalized.json")
        if set(spec_res) != set(norm_res):
            errors.append(f"resource IDs differ between ② and ③: {sorted(set(spec_res) ^ set(norm_res))}")
        for rid in set(spec_res) & set(norm_res):
            s_keys, n_keys = set(spec_res[rid]["settings"]), set(norm_res[rid]["settings"])
            if s_keys != n_keys:
                errors.append(f"{rid}: setting keys differ between ② and ③: {sorted(s_keys ^ n_keys)}")
            for dep in norm_res[rid].get("dependsOn", []):
                if dep not in norm_res:
                    errors.append(f"{rid}: dependsOn unknown resource {dep}")
        if set(spec["target"]) != set(norm["target"]):
            errors.append("target keys differ between ② and ③")
        if set(spec.get("tags") or {}) != set(norm.get("tags") or {}):
            errors.append("tag keys differ between ② and ③")

        # ---- 4. every field: traceable, resolved, or asked about ------------
        issue_text = (work / "issue-report.md").read_text(encoding="utf-8")
        field_paths = []
        for path, f in iter_fields(norm):
            field_paths.append(path)
            unknown = [s for s in f["sources"] if s not in params]
            if unknown:
                errors.append(f"{path}: unknown source IDs {unknown}")
            status = f["status"]
            if status in RESOLVED:
                if f["value"] is None:
                    errors.append(f"{path}: status '{status}' but value is null")
                if not f["sources"]:
                    errors.append(f"{path}: status '{status}' without sources — every value must trace to a document")
                if status == "answered" and not any(
                    s in params and params[s]["sourceRef"]["path"].endswith("answers.md") for s in f["sources"]
                ):
                    errors.append(f"{path}: status 'answered' but no source comes from answers.md")
            else:
                blocking.append(f"{path} [{status}]")
                if f"`{path}`" not in issue_text:
                    errors.append(f"{path}: unresolved but not listed in issue-report.md (expected `{path}`)")
                # `missing` means the design says nothing. Citing a source that does
                # state a value contradicts that, and produces a question whose own
                # 現状の記載 line is the answer. (`ambiguous` and `conflict` are
                # different: those legitimately cite stated-but-unusable values.)
                if status == "missing":
                    stated = [
                        s for s in f["sources"]
                        if s in params and not GAP_MARKERS.search(str(params[s]["rawValue"]))
                    ]
                    if stated:
                        quoted = ", ".join(f"{s}={params[s]['rawValue']!r}" for s in stated)
                        errors.append(
                            f"{path}: status 'missing' but its sources state a value ({quoted}) — "
                            "normalize it, or use 'ambiguous'/'conflict' if it cannot be mapped"
                        )

        scope = norm["target"]["scope"]
        if scope["status"] in RESOLVED:
            if scope["value"] not in SCOPES:
                errors.append(f"target:scope must be one of {sorted(SCOPES)}, got {scope['value']!r}")
            elif scope["value"] == "resourceGroup" and "resourceGroup" not in norm["target"]:
                errors.append("target:scope is resourceGroup but target:resourceGroup is absent")

        # ---- 5. traceability -------------------------------------------------
        with (work / "traceability.csv").open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames != TRACE_COLUMNS:
                errors.append(f"traceability.csv header must be: {','.join(TRACE_COLUMNS)}")
                rows = []
            else:
                rows = list(reader)
        traced = {r["field_path"]: r for r in rows}
        untraced = [p for p in field_paths if p not in traced]
        if untraced:
            errors.append(f"fields missing from traceability.csv: {untraced[:10]}{' …' if len(untraced) > 10 else ''}")
        for p, row in traced.items():
            if p in field_paths:
                expected = next(f["status"] for fp, f in iter_fields(norm) if fp == p)
                if row["status"] != expected:
                    errors.append(f"traceability.csv status for {p} is '{row['status']}', normalized.json says '{expected}'")

        # ---- 6. nothing extracted in ① was silently dropped -------------------
        # ② and ③ agreeing proves only that they match each other; a requirement
        # both dropped leaves no trace at all. So check ① → ②③ as well: every
        # parameter must reach a field, be consumed as a resource name, or be
        # asked about. Otherwise a security control can vanish between ① and ②
        # while the gate still reports a clean BLOCKED.
        used = {s for doc in (norm, spec) for _, f in iter_fields(doc) for s in f["sources"]}
        logical_names = {r.get("logicalName") for r in norm["resources"]}
        dropped = [
            f"{pid} ({params[pid]['label']})"
            for pid in params
            if pid not in used
            and params[pid]["rawValue"] not in logical_names
            and not re.search(rf"\b{re.escape(pid)}\b", issue_text)
        ]
        if dropped:
            errors.append(
                "extracted but neither used nor asked about — re-run agent2-extract: "
                f"{dropped[:10]}{' …' if len(dropped) > 10 else ''}"
            )

        # ---- 7. infra phase --------------------------------------------------
        if phase == "infra":
            for name in ("main.bicep", "main.bicepparam"):
                if not (infra / name).exists():
                    errors.append(f"missing: {rel(infra / name)}")
            no_ref = [r["field_path"] for r in rows if r["status"] in RESOLVED and not r["bicep_ref"].strip()]
            if no_ref:
                errors.append(f"traceability rows without bicep_ref: {no_ref[:10]}{' …' if len(no_ref) > 10 else ''}")

    except (KeyError, TypeError, AttributeError) as e:
        errors.append(f"artifact structure invalid ({type(e).__name__}: {e}) — install jsonschema for details")

    return errors, blocking, notes


def main() -> int:
    # Windows consoles use the locale code page (cp932 on Japanese systems), which
    # can encode neither the em dashes nor 差戻し below. CI is already UTF-8.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--phase", choices=["spec", "infra"], default="spec")
    args = ap.parse_args()

    errors, blocking, notes = check(args.project, args.phase)

    print(f"Agent2 gate — project={args.project} phase={args.phase}")
    for n in notes:
        print(f"  note: {n}")
    if blocking:
        print(f"\nUnresolved fields ({len(blocking)}):")
        for b in blocking:
            print(f"  - {b}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print("\nRESULT: BROKEN — fix the artifacts or re-run agent2-extract")
        return 2
    if blocking:
        print("\nRESULT: BLOCKED — 差戻し: send work/%s/issue-report.md to the design team" % args.project)
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
