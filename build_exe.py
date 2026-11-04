import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: list, cwd: Path = None) -> bool:
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode == 0


def main():
    root = Path(__file__).parent

    print("=" * 50)
    print("Building surreal-namer executable")
    print("=" * 50)

    print("\n[1/3] Installing dependencies...")
    if not run_cmd([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=root):
        print("Failed to install dependencies")
        return 1

    print("\n[2/3] Building executable with PyInstaller...")
    if not run_cmd([sys.executable, "-m", "PyInstaller", "build.spec", "--clean"], cwd=root):
        print("Build failed")
        return 1

    print("\n[3/3] Verifying output...")
    exe_path = root / "dist" / "surreal-namer.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\nBuild successful!")
        print(f"  Executable: {exe_path}")
        print(f"  Size: {size_mb:.1f} MB")
        return 0
    else:
        print("\nExecutable not found at expected location")
        return 1


if __name__ == "__main__":
    sys.exit(main())