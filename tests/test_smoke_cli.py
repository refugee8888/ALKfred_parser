import subprocess
import sys


def test_cli_help_runs(monkeypatch):
    proc = subprocess.run(
        [sys.executable, "-m", "alkfred.cli.build", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )

    # Validate it ran without crashing
    assert proc.returncode == 0
    assert "Welcome to ALKfred" in proc.stdout
