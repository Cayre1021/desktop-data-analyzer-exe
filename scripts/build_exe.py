from pathlib import Path
import subprocess
import sys


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    spec_path = project_root / "desktop-data-analyzer.spec"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        str(spec_path),
    ]
    return subprocess.call(command, cwd=project_root)


if __name__ == "__main__":
    raise SystemExit(main())
