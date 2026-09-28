"""本文がごく少ないページ（ほぼ空白ページ）を検出する．"""
import pathlib, fitz
W = pathlib.Path(__file__).parent
d = fitz.open(W / "build" / "医療統計学参考書.pdf")
for i, p in enumerate(d):
    blocks = [b for b in p.get_text("blocks") if b[1] > 60 and b[3] < p.rect.height - 40]  # 柱とノンブルを除く
    if not blocks:
        continue
    bottom = max(b[3] for b in blocks)
    frac = (bottom - 60) / (p.rect.height - 100)
    if frac < 0.30:
        first = blocks[0][4].strip().replace("\n", " ")[:50]
        print(f"PDF p{i+1} (idx {i}): 使用率 {frac:.0%}  先頭: {first}")
