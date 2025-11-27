import subprocess
import sys

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





    



