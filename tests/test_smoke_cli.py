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


# def test_cli_overwrite_runs(monkeypatch):
#     monkeypatch.setattr(
#         "alkfred.etl.civic_fetch.fetch_civic_evidence",
#         lambda *a, **kw: [{"id": 1, "molecularProfile": {"name": "ALK test"}}],
#     )

#     # Run the CLI in a subprocess so argparse is parsed naturally
#     proc = subprocess.run(
#         [
#             sys.executable,
#             "-m",
#             "alkfred.cli.build",
#             "--overwrite",
#             "--source",
#             "civic",
#             "--limit",
#             "1",
#         ],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#     )

#     # Helpful output if it fails
#     if proc.returncode != 0:
#         print("\nSTDOUT:\n", proc.stdout)
#         print("\nSTDERR:\n", proc.stderr)

#     # Validate it ran without crashing
#     assert proc.returncode == 0


def test_cli_overwrite_runs(tmp_path):
    curated = tmp_path / "curated.json"
    raw = tmp_path / "raw.json"
    db = tmp_path / "alkfred.sqlite"

    # tiny curated fixture so build can run without fetching
    curated.write_text('{"DOID:3908||v-alk fusion": {"therapies":[{"name":"alectinib","ncit_id":"C113655"}], "evidence_count":1, "disease_doid":"3908", "gene_symbol":"v::ALK Fusion"}}')

    proc = subprocess.run(
        [
            sys.executable, "-m", "alkfred.cli.build",
            "--source", "curated",
            "--curated", str(curated),
            "--raw", str(raw),
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



    



