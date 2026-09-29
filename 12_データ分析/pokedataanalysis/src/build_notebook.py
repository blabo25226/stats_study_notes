"""各章の md + py を結合して pokedataanalysis.ipynb を生成する.

対応ルール
----------
- 1章 = ``chNN_<英語名>.md`` + ``chNN_<英語名>.py`` の組。
- md は ``<!-- cell: NN-k -->`` の行で区切る。最初の区切りより前は章の導入文（概要）。
  k は英数字（例: ``11-0`` 使うデータ, ``11-1`` 節, ``11-1r`` 結果の読み方, ``11-end`` まとめ）。
  書き方のひな形は ``_template.md``。
- py は ``# %% NN-k`` の行で区切る。最初の区切りより前（import など）は単体実行用で、
  ipynb には入れない（共通処理 poke.py と ``df = load_data()`` は ipynb の先頭に入る）。
- ipynb 内では md NN-k → py NN-k の順に並ぶ。md 側の ID の順序が基準で、
  md にしかない ID（解説のみ）は許すが、py にしかない ID はエラーにする。

使い方
------
    python build_notebook.py              # 全章を結合して ../pokedataanalysis.ipynb に保存
    python build_notebook.py --execute    # 結合後に全セルを実行して出力も保存
    python build_notebook.py --check      # 対応ルールの検査だけ行う
    python build_notebook.py -c 0 1 2     # 指定した章だけ結合（確認用）
"""
import argparse
import re
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

SRC = Path(__file__).resolve().parent
OUT = SRC.parent / "pokedataanalysis.ipynb"

MD_MARK = re.compile(r"^<!--\s*cell:\s*(\d{2}-[0-9A-Za-z]+)\s*-->\s*$", re.M)
PY_MARK = re.compile(r"^# %%\s+(\d{2}-[0-9A-Za-z]+)\s*$", re.M)

HEADER = """# ポケモンデータで学ぶ統計検定準1級

『統計検定準1級』の出題範囲の各章について、ポケモン（USUM・920匹）のデータで分析を行う。

- データ: `90_data/processed_poke_data_USUM.csv`
- ソース: `12_データ分析/pokedataanalysis/src/`（このノートブックは `build_notebook.py` で自動生成）
- 対象外の章: 第14章 マルコフ連鎖、第15章 確率過程の基礎、第27章 時系列解析（データに時間構造がないため）
"""


def split(text, pattern):
    """区切り行で分割し、(前置き, [(ID, 本文), ...]) を返す."""
    marks = list(pattern.finditer(text))
    head = text[: marks[0].start()] if marks else text
    blocks = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        blocks.append((m.group(1), text[m.end():end].strip("\n")))
    return head.strip("\n"), blocks


def chapters(selected=None):
    """(章番号, md パス, py パス) を章番号順に返す."""
    result = []
    for md in sorted(SRC.glob("ch[0-9][0-9]_*.md")):
        no = int(md.name[2:4])
        if selected is not None and no not in selected:
            continue
        result.append((no, md, md.with_suffix(".py")))
    return result


def check_chapter(no, md, py):
    """対応ルールを検査し、エラーメッセージのリストを返す."""
    errors = []
    if not py.exists():
        return [f"{md.name}: 対応する {py.name} がない"]
    _, md_blocks = split(md.read_text(encoding="utf-8"), MD_MARK)
    _, py_blocks = split(py.read_text(encoding="utf-8"), PY_MARK)
    md_ids = [i for i, _ in md_blocks]
    py_ids = [i for i, _ in py_blocks]
    for name, ids in [(md.name, md_ids), (py.name, py_ids)]:
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            errors.append(f"{name}: ID が重複 {sorted(dup)}")
        bad = [i for i in ids if int(i[:2]) != no]
        if bad:
            errors.append(f"{name}: 章番号と合わない ID {bad}")
    only_py = [i for i in py_ids if i not in md_ids]
    if only_py:
        errors.append(f"{py.name}: md に対応する区切りがない ID {only_py}")
    return errors


def common_code():
    """poke.py の本体（最初の ``# %%`` 以降）を返す."""
    text = (SRC / "poke.py").read_text(encoding="utf-8")
    return text.split("# %%", 1)[1].strip("\n")


def build(selected=None):
    nb = new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    cells = [
        new_markdown_cell(HEADER),
        new_markdown_cell("## 共通処理\n\n`src/poke.py` の内容。データの読込・前処理と描画設定を行う。"),
        new_code_cell(common_code()),
        new_code_cell("df = load_data()\ndf.shape"),
    ]
    for no, md, py in chapters(selected):
        md_head, md_blocks = split(md.read_text(encoding="utf-8"), MD_MARK)
        _, py_blocks = split(py.read_text(encoding="utf-8"), PY_MARK)
        code = dict(py_blocks)
        if md_head:
            cells.append(new_markdown_cell(md_head))
        for cid, text in md_blocks:
            if text:
                cells.append(new_markdown_cell(text))
            if code.get(cid):
                cells.append(new_code_cell(code[cid]))
    nb.cells = cells
    return nb


def execute(nb, workdir):
    import os

    from nbclient import NotebookClient

    # MPLBACKEND=Agg が残っているとカーネルがインライン表示にならず図が保存されない
    os.environ.pop("MPLBACKEND", None)
    NotebookClient(nb, timeout=600, kernel_name="python3",
                   resources={"metadata": {"path": str(workdir)}}).execute()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-c", "--chapters", type=int, nargs="+", help="結合する章番号")
    ap.add_argument("--execute", action="store_true", help="全セルを実行して出力を保存")
    ap.add_argument("--check", action="store_true", help="検査のみ")
    ap.add_argument("-o", "--output", type=Path, default=OUT, help="出力先")
    args = ap.parse_args()

    selected = set(args.chapters) if args.chapters else None
    targets = chapters(selected)
    errors = [e for t in targets for e in check_chapter(*t)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    print(f"検査OK: {len(targets)}章 ({', '.join(t[1].stem for t in targets)})")
    if args.check:
        return

    nb = build(selected)
    if args.execute:
        execute(nb, OUT.parent)  # 出力先によらずノートブックの本来の場所で実行
    args.output.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, args.output)
    print(f"保存: {args.output}  ({len(nb.cells)} セル{'・実行済み' if args.execute else ''})")


if __name__ == "__main__":
    main()
