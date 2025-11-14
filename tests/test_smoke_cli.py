from pdb import run
import subprocess
import sys
from _pytest import monkeypatch
from _pytest.fixtures import FixtureRequest
import pytest
from alkfred.cli import build
import os

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


def test_cli_overwrite_runs(tmp_path):
    
    civic_path = tmp_path / "civic.json"
    db = tmp_path / "alkfred.sqlite"

    # tiny curated fixture so build can run without fetching
    civic_path.write_text('{"DOID:3908||v-alk fusion": {"therapies":[{"name":"alectinib","ncit_id":"C113655"}], "evidence_count":1, "disease_doid":"3908", "gene_symbol":"v::ALK Fusion"}}')
    
    proc = subprocess.run(
        [
            sys.executable, "-m", "alkfred.cli.build",
            "--source", "test",
            "--testcivic", str(civic_path),
            "--db", str(db),
            "--overwrite",
            "--verbose",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "ALKFRED_TEST_MODE": "1"},  # optional guard
    )

    assert proc.returncode == 0, proc.stderr
    assert db.exists



    



