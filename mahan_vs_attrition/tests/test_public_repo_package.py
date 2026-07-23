"""Tests for public repo package integrity."""

from pathlib import Path


def test_public_repo_handoff_exists():
    assert Path("PUBLIC_REPO_HANDOFF.md").exists()


def test_blind_validation_cases_included():
    assert Path("data/blind_validation_cases.yml").exists()


def test_manifest_has_no_stale_web_entries():
    manifest = Path("PUBLIC_REPO_MANIFEST.txt").read_text()
    assert "./web/" not in manifest
    assert not any(line.startswith("./web") for line in manifest.splitlines())


def test_no_latex_build_trash_in_public_package():
    forbidden = [
        "paper/manuscript.aux",
        "paper/manuscript.blg",
        "paper/manuscript.log",
        "paper/manuscript.out",
    ]
    for f in forbidden:
        assert not Path(f).exists(), f"{f} should not be in public repo"
