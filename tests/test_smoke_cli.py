import subprocess
import sys

def test_cli_help_runs():
    # python -m alkfred.cli.build --help
    proc = subprocess.run(
        [sys.executable, "-m", "alkfred.cli.build", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.returncode == 0
    assert "Welcome to ALKfred" in proc.stdout

def test_cli_overwrite_runs():
    # python -m alkfred.cli.build --overwrite
    proc = subprocess.run(
        [sys.executable, "-m", "alkfred.cli.build", "--overwrite", "--source","civic", "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print("STDOUT:\n", proc.stdout)
        print("STDERR:\n", proc.stderr)
    assert proc.returncode == 0


    



    



