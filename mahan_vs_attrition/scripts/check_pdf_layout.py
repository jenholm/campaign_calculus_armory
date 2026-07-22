#!/usr/bin/env python3
"""Fail the paper build on blank pages, major overflow, and stale float damage."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def pdf_pages(pdf: Path) -> int:
    info = run(["pdfinfo", str(pdf)])
    match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not read PDF page count")
    return int(match.group(1))


def page_text(pdf: Path, page: int) -> str:
    return run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"])


def is_effectively_blank(text: str, page: int) -> bool:
    cleaned = re.sub(r"\s+", "", text)
    cleaned = cleaned.replace(str(page), "")
    return len(cleaned) == 0


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_pdf_layout.py manuscript.pdf manuscript.log", file=sys.stderr)
        return 2

    pdf = Path(sys.argv[1])
    log = Path(sys.argv[2])

    pages = pdf_pages(pdf)
    errors: list[str] = []

    for page in range(1, pages + 1):
        text = page_text(pdf, page)
        if is_effectively_blank(text, page):
            errors.append(f"blank page detected: PDF page {page}")

    log_text = log.read_text(errors="replace")

    bad_patterns = [
        r"Overfull \\hbox \((?:[1-9]\d+|\d{3,})\.",
        r"Overfull \\vbox",
        r"Float too large",
        r"multiply defined",
        r"undefined references",
        r"undefined citations",
    ]

    for pattern in bad_patterns:
        for match in re.finditer(pattern, log_text, flags=re.IGNORECASE):
            errors.append(f"LaTeX log issue: {match.group(0)}")

    if errors:
        print("PDF layout gate FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"PDF layout gate passed: {pages} pages, no blank pages, no major overflow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
