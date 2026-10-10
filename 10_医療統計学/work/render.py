"""PDF の指定ページ（またはキーワードを含む最初のページ）を PNG に書き出す確認用スクリプト．
使い方: python render.py 図12.1 図15.1 ...   または   python render.py p10 p11
        python render.py all            # 全ページを build/pages/ に書き出す（目視確認用）
"""
import sys, pathlib, fitz
here = pathlib.Path(__file__).parent
d = fitz.open(here / "build" / "医療統計学参考書.pdf")
if sys.argv[1:] == ["all"]:
    out_dir = here / "build" / "pages"
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob("p*.png"):
        old.unlink()
    for i, page in enumerate(d):
        page.get_pixmap(dpi=80).save(out_dir / f"p{i + 1:03d}.png")
    print(f"{len(d)} pages -> {out_dir}")
    sys.exit()
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
