import subprocess
from pathlib import Path

from utils.logging import ts


def run_cmd(cmd: list[str], cwd: Path) -> None:
    """Run a command from a given working directory."""
    print(f"[{ts()}] Running: {' '.join(cmd)}  (cwd = {cwd})")
    subprocess.run(cmd, cwd = str(cwd), check = True)
