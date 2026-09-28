"""PDF の指定ページ（またはキーワードを含む最初のページ）を PNG に書き出す確認用スクリプト．
使い方: python render.py 図12.1 図15.1 ...   または   python render.py p10 p11
"""
import sys, pathlib, fitz
here = pathlib.Path(__file__).parent
d = fitz.open(here / "build" / "医療統計学参考書.pdf")
for arg in sys.argv[1:]:
    if arg.startswith("p") and arg[1:].isdigit():
        idx = int(arg[1:])
    else:
        key = arg.replace("図", "図 ").replace("  ", " ")
        idx = next((i for i, p in enumerate(d) if key in p.get_text()), None)
        if idx is None:
            print("not found", arg); continue
    out = here / "build" / f"v_{idx}.png"
    d[idx].get_pixmap(dpi=80).save(out)
    print(arg, "-> page", idx, out)
