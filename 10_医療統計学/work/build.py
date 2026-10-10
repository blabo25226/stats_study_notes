"""作業用パーツを連結して 10_医療統計学/医療統計学参考書.tex を生成し，LuaLaTeX でコンパイルする。

使い方:
    python build.py            # 連結のみ
    python build.py compile    # 連結 + lualatex 3回（work/build に出力）．警告があれば非0で終了
"""
import pathlib
import re
import subprocess
import sys

WORK = pathlib.Path(__file__).resolve().parent
PARTS = WORK / "parts"
OUT = WORK.parent / "医療統計学参考書.tex"
BUILD = WORK / "build"

ORDER = [
    "00_preamble.tex",
    "01_front.tex",
    # ch11（競合リスク）は ch10 に統合，ch15（メタアナリシス）は削除
    *[f"ch{i:02d}.tex" for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 16, 17)],
    "90_appendix.tex",
    "99_bib.tex",
]


def concat() -> None:
    chunks = []
    for name in ORDER:
        p = PARTS / name
        if not p.exists():
            raise SystemExit(f"missing part: {name}")
        text = p.read_text(encoding="utf-8").rstrip() + "\n"
        chunks.append(f"% ===== {name} =====\n" + text)
    body = "\n".join(chunks)
    if "\\begin{document}" not in body:
        raise SystemExit("front matter missing \\begin{document}")
    body += "\n\\end{document}\n"
    OUT.write_text(body, encoding="utf-8")
    print(f"wrote {OUT} ({len(body.encode('utf-8'))} bytes)")


def compile_pdf(runs: int = 3) -> None:
    BUILD.mkdir(exist_ok=True)
    for i in range(runs):
        r = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory=work/build", OUT.name],
            cwd=OUT.parent, capture_output=True)
        print(f"run {i+1}: exit {r.returncode}")
        if r.returncode != 0:
            tail = r.stdout[-4000:].decode("utf-8", "replace")
            print(tail)
            raise SystemExit(1)
    log = (BUILD / (OUT.stem + ".log")).read_text(encoding="utf-8", errors="replace")
    if report(log):
        raise SystemExit("build has warnings (see above)")


def report(log: str) -> int:
    """警告を表示し，overfull 以外の警告の総数を返す．"""
    pats = {
        "undefined": r"Undefined control sequence",
        "undef_ref": r"Reference `[^']+' on page \d+ undefined",
        "undef_cite": r"Citation `[^']+' on page \d+ undefined",
        "multiply": r"multiply defined",
        "overfull": r"Overfull \\hbox \((\d+\.\d+)pt too wide\)",
        "missing_char": r"Missing character",
        "rerun": r"Rerun to get",
    }
    errors = 0
    for k, pat in pats.items():
        found = re.findall(pat, log)
        if k == "overfull":
            big = [float(x) for x in found if float(x) > 5.0]
            print(f"{k}: {len(found)} total, {len(big)} > 5pt, max {max(map(float, found), default=0):.1f}pt")
            for m in re.finditer(r"Overfull \\hbox \((\d+\.\d+)pt too wide\)[^\n]*?lines (\d+)--(\d+)", log):
                if float(m.group(1)) > 5.0:
                    print(f"   {m.group(1)}pt at lines {m.group(2)}--{m.group(3)}")
        else:
            print(f"{k}: {len(found)}")
            errors += len(found)
    for m in re.finditer(r"(Reference|Citation) `([^']+)' on page (\d+) undefined", log):
        print("  ", m.group(0))
    return errors


if __name__ == "__main__":
    concat()
    if len(sys.argv) > 1 and sys.argv[1] == "compile":
        compile_pdf()
