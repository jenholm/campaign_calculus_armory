"""Check manuscript consistency: undefined refs, quantitative claims, terminology checks."""

import json
import re
import sys
from pathlib import Path


def collect_tex_files() -> dict[str, str]:
    """Return {relative_path: text} for manuscript.tex and all sections/*.tex."""
    root = Path(__file__).resolve().parent.parent
    files: dict[str, str] = {}
    main = root / "paper" / "manuscript.tex"
    files[str(main.relative_to(root))] = main.read_text()
    for tex in sorted((root / "paper" / "sections").glob("*.tex")):
        files[str(tex.relative_to(root))] = tex.read_text()
    for tex in sorted((root / "paper" / "sections" / "generated").glob("*.tex")):
        files[str(tex.relative_to(root))] = tex.read_text()
    for tex in sorted((root / "paper" / "tables").glob("*.tex")):
        files[str(tex.relative_to(root))] = tex.read_text()
    return files


def find_labels(files: dict[str, str]) -> dict[str, str]:
    """Map label name -> file where it is defined."""
    labels: dict[str, str] = {}
    pattern = re.compile(r"\\label\{([^}]+)\}")
    for path, text in files.items():
        for m in pattern.finditer(text):
            labels[m.group(1)] = path
    return labels


def find_refs(files: dict[str, str]) -> list[tuple[str, str, int]]:
    """Return list of (ref_name, file, line_number) for every \\ref{...}."""
    refs: list[tuple[str, str, int]] = []
    pattern = re.compile(r"\\ref\{([^}]+)\}")
    for path, text in files.items():
        for m in pattern.finditer(text):
            line = text[: m.start()].count("\n") + 1
            refs.append((m.group(1), path, line))
    return refs


def check_undefined_refs(
    labels: dict[str, str], refs: list[tuple[str, str, int]]
) -> list[dict]:
    issues = []
    for ref_name, ref_file, line in refs:
        if ref_name not in labels:
            issues.append({
                "type": "undefined_reference",
                "ref": ref_name,
                "file": ref_file,
                "line": line,
            })
    return issues


def extract_quantitative_claims(files: dict[str, str]) -> dict[str, list[dict]]:
    """Extract percentages, counts, and ratios with surrounding context."""
    claims: dict[str, list[dict]] = {}
    pct_re = re.compile(
        r"(\d+(?:\.\d+)?)\s*\\%"
    )
    count_re = re.compile(
        r"(\d[\d,]*)\s+(?:wars?|battles?|conflicts?|cases?|cases|presets|coefficients|components|countries|observed|features)"
    )
    for path, text in files.items():
        for m in pct_re.finditer(text):
            val = m.group(1)
            line = text[: m.start()].count("\n") + 1
            claims.setdefault(val + r"\%", []).append({
                "file": path,
                "line": line,
                "context": text[max(0, m.start() - 60) : m.end() + 60].replace("\n", " "),
            })
        for m in count_re.finditer(text):
            val = m.group(1).replace(",", "")
            line = text[: m.start()].count("\n") + 1
            claims.setdefault(val, []).append({
                "file": path,
                "line": line,
                "context": text[max(0, m.start() - 60) : m.end() + 60].replace("\n", " "),
            })
    return claims


def check_86_percent(files: dict[str, str]) -> dict:
    """Check that 86% claim appears at most twice."""
    pattern = re.compile(r"86(?:\.0)?\\%")
    occurrences = []
    for path, text in files.items():
        for m in pattern.finditer(text):
            line = text[: m.start()].count("\n") + 1
            context = text[max(0, m.start() - 80) : m.end() + 80].replace("\n", " ")
            occurrences.append({"file": path, "line": line, "context": context})
    issue = None
    if len(occurrences) > 2:
        issue = {
            "type": "86_percent_too_many",
            "count": len(occurrences),
            "occurrences": occurrences,
            "message": f"86% appears {len(occurrences)} times (max allowed: 2)",
        }
    return {"count": len(occurrences), "occurrences": occurrences, "issue": issue}


def check_wwii_negotiated(files: dict[str, str]) -> list[dict]:
    """Check WWII is not labeled 'Negotiated settlement'."""
    issues = []
    # Look for lines mentioning WWII/World War II + Negotiated settlement
    wwii_patterns = [
        re.compile(r"(?:WWII|World War II|World War 2)\b.*?(?:Negotiated|negotiated)", re.IGNORECASE),
        re.compile(r"(?:Negotiated|negotiated).*?(?:WWII|World War II|World War 2)\b", re.IGNORECASE),
    ]
    for path, text in files.items():
        for pat in wwii_patterns:
            for m in pat.finditer(text):
                line = text[: m.start()].count("\n") + 1
                issues.append({
                    "type": "wwii_negotiated_settlement",
                    "file": path,
                    "line": line,
                    "match": m.group(),
                    "message": "WWII should not be labeled 'Negotiated settlement'",
                })
    return issues


def check_mahan_mechanism(files: dict[str, str]) -> list[dict]:
    """Check that 'Mahan mechanism' has been replaced with 'decisive shock mechanism'."""
    issues = []
    pattern = re.compile(r"Mahan mechanism", re.IGNORECASE)
    for path, text in files.items():
        for m in pattern.finditer(text):
            line = text[: m.start()].count("\n") + 1
            issues.append({
                "type": "mahan_mechanism_not_replaced",
                "file": path,
                "line": line,
                "match": m.group(),
                "message": "'Mahan mechanism' should be replaced with 'decisive shock mechanism'",
            })
    return issues


def main() -> int:
    files = collect_tex_files()
    labels = find_labels(files)
    refs = find_refs(files)

    all_issues: list[dict] = []

    # 1. Undefined references
    undefined = check_undefined_refs(labels, refs)
    all_issues.extend(undefined)

    # 2. Quantitative claims (informational)
    claims = extract_quantitative_claims(files)

    # 3. 86% check
    pct_86 = check_86_percent(files)
    if pct_86["issue"]:
        all_issues.append(pct_86["issue"])

    # 4. WWII + Negotiated settlement
    wwii_issues = check_wwii_negotiated(files)
    all_issues.extend(wwii_issues)

    # 5. Mahan mechanism check
    mahan_issues = check_mahan_mechanism(files)
    all_issues.extend(mahan_issues)

    # Build report
    report = {
        "summary": {
            "files_scanned": len(files),
            "labels_found": len(labels),
            "refs_found": len(refs),
            "undefined_refs": len(undefined),
            "86_percent_count": pct_86["count"],
            "wwii_negotiated_issues": len(wwii_issues),
            "mahan_mechanism_issues": len(mahan_issues),
            "total_issues": len(all_issues),
        },
        "undefined_references": undefined,
        "86_percent": {
            "count": pct_86["count"],
            "occurrences": pct_86["occurrences"],
        },
        "wwii_negotiated_settlement": wwii_issues,
        "mahan_mechanism_remaining": mahan_issues,
        "quantitative_claims_by_value": {
            k: [{"file": c["file"], "line": c["line"]} for c in v]
            for k, v in sorted(claims.items())
        },
        "issues": all_issues,
    }

    print(json.dumps(report, indent=2))
    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
