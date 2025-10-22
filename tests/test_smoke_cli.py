from pdb import run
import subprocess
import sys
from _pytest import monkeypatch
from _pytest.fixtures import FixtureRequest
import pytest
from alkfred.cli import build

def test_cli_help_runs(monkeypatch):
    monkeypatch.setattr("alkfred.cli.build", lambda *a: "--help")
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "alkfred.cli.build",
            "--help",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Validate it ran without crashing
    assert proc.returncode == 0
    assert "Welcome to ALKfred" in proc.stdout


def test_cli_overwrite_runs(monkeypatch):
    monkeypatch.setattr(
        "alkfred.etl.civic_fetch.fetch_civic_evidence",
        lambda *a, **kw: [{"id": 1, "molecularProfile": {"name": "ALK test"}}],
    )

    # Run the CLI in a subprocess so argparse is parsed naturally
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "alkfred.cli.build",
            "--overwrite",
            "--source",
            "civic",
            "--limit",
            "1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Helpful output if it fails
    if proc.returncode != 0:
        print("\nSTDOUT:\n", proc.stdout)
        print("\nSTDERR:\n", proc.stderr)

    # Validate it ran without crashing
    assert proc.returncode == 0


    



    



