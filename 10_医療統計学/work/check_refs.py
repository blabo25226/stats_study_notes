"""参照の種類と PDF 上の表記を検査する．"""
import pathlib, re, collections, fitz
W = pathlib.Path(__file__).parent
aux = (W / "build" / "医療統計学参考書.aux").read_text(encoding="utf-8", errors="replace")
want = {"prop": "meidai", "thm": "teiri", "def": "teigi", "reidai": "reidai", "app": "appendix"}
bad = collections.Counter(); ok = collections.Counter()
for lab, typ in re.findall(r"\\newlabel\{([a-z]+:[^@}]*)@cref\}\{\{\[([a-z]+)\]", aux):
    pre = lab.split(":")[0]
    if pre in want:
        (ok if typ == want[pre] else bad)[(pre, typ)] += 1
print("ok:", dict(ok)); print("BAD:", dict(bad))
toc = (W / "build" / "医療統計学参考書.toc").read_text(encoding="utf-8", errors="replace")
print("toc 参考文献:", toc.count("参考文献"))
d = fitz.open(W / "build" / "医療統計学参考書.pdf")
txt = "\n".join(p.get_text() for p in d)
for pat in [r"第\s*[A-E]\s*章", r"付録\s*[A-E]"]:
    print(pat, len(re.findall(pat, txt)))
# 「定義 x.y」と書かれている番号が本当に定義かを確認
defs = set(re.findall(r"定義\s*(\d+\.\d+)（", txt)) | set(re.findall(r"定義\s*(\d+\.\d+)\s", txt))
kinds = {}
for kind in ["定義", "命題", "定理"]:
    for m in re.finditer(kind + r"\s*(\d+\.\d+)", txt):
        kinds.setdefault(m.group(1), set()).add(kind)
mixed = {k: v for k, v in kinds.items() if len(v) > 1}
print("同じ番号に複数の種類名:", mixed)
