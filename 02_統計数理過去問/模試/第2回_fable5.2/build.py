"""Build the three PDFs with LuaLaTeX; keep auxiliary files in 93_scratch.

Run: python build.py
Requires LuaLaTeX and ltjsarticle. Source files are UTF-8.
日本語ファイル名の処理を安定させるため、93_scratch/sm_mock2_build/ に英数字名でコピーして
各冊子を2回コンパイルし、PDFをこのフォルダへ戻す。
"""
from pathlib import Path
import os
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILD = ROOT / "93_scratch" / "sm_mock2_build"
STYLE = "sm_mock_style.tex"
BOOKLETS = {"problem": "問題", "solutions": "模範解答", "rubric": "採点基準"}


def main():
    executable = shutil.which("lualatex")
    if not executable:
        raise SystemExit("LuaLaTeX was not found on PATH.")
    BUILD.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / STYLE, BUILD / STYLE)
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "1794438000"
    total = 0
    for job, label in BOOKLETS.items():
        stem = f"SM_第2回_fable5.2_{label}"
        shutil.copy2(HERE / f"{stem}.tex", BUILD / f"{job}.tex")
        for run in range(2):
            proc = subprocess.run(
                [executable, "-no-shell-escape", "-interaction=nonstopmode",
                 "-halt-on-error", "-file-line-error", f"{job}.tex"],
                cwd=BUILD, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            (BUILD / f"{job}.run{run + 1}.txt").write_bytes(proc.stdout)
            if proc.returncode:
                print(proc.stdout.decode("utf-8", errors="replace")[-6000:])
                raise SystemExit(f"Build failed: {job}, pass {run + 1}")
        shutil.copy2(BUILD / f"{job}.pdf", HERE / f"{stem}.pdf")
        log = (BUILD / f"{job}.log").read_text(encoding="utf-8", errors="replace")
        issues = [line for line in log.splitlines()
                  if any(s in line for s in ("Overfull", "Underfull", "Warning", "Missing character"))]
        pages = [line for line in log.splitlines() if line.startswith("Output written")]
        print(f"{stem}.pdf: {len(issues)} layout/warning lines; {pages[-1] if pages else ''}")
        for line in issues:
            print("  ", line)
        total += len(issues)
    print("total layout/warning lines:", total)


if __name__ == "__main__":
    main()
