"""Build the three PDFs with LuaLaTeX; keep auxiliary files in 93_scratch.

Run: python build.py
Requires LuaLaTeX and ltjsarticle. Source files are UTF-8.
"""
from pathlib import Path
import os
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILD = ROOT / "93_scratch" / "sm_mock1_build"
BOOKLETS = {"problem": "問題", "solutions": "模範解答", "rubric": "採点基準"}


def main():
    executable = shutil.which("lualatex")
    if not executable:
        raise SystemExit("LuaLaTeX was not found on PATH.")
    BUILD.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "sm_mock_style.tex", BUILD / "sm_mock_style.tex")
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "1794351600"
    for job, label in BOOKLETS.items():
        stem = f"SM_第1回_6astra_{label}"
        shutil.copy2(HERE / f"{stem}.tex", BUILD / f"{job}.tex")
        for run in range(2):
            proc = subprocess.run(
                [executable, "-no-shell-escape", "-interaction=nonstopmode",
                 "-halt-on-error", "-file-line-error", f"{job}.tex"],
                cwd=BUILD, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            (BUILD / f"{job}.run{run + 1}.txt").write_bytes(proc.stdout)
            if proc.returncode:
                print(proc.stdout.decode("utf-8", errors="replace")[-9000:])
                raise SystemExit(f"Build failed: {job}, pass {run + 1}")
        shutil.copy2(BUILD / f"{job}.pdf", HERE / f"{stem}.pdf")
        log = (BUILD / f"{job}.log").read_text(encoding="utf-8", errors="replace")
        issues = [line for line in log.splitlines()
                  if any(s in line for s in ("Overfull", "Underfull", "Warning", "Missing character"))]
        print(f"{stem}.pdf: {len(issues)} layout/warning lines")
        for line in issues:
            print(line)


if __name__ == "__main__":
    main()
