"""ポケモンデータ分析の共通処理（データ読込・前処理・描画設定）.

各章の .py は ``from poke import *`` で読み込む。
build_notebook.py はこのファイルの内容を ipynb の先頭セルにそのまま埋め込む。
"""
# %%
import os
import re
from pathlib import Path

# Windows で sklearn(joblib) が物理コア数の警告を大量に出すのを抑える
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

try:
    import japanize_matplotlib  # noqa: F401  日本語フォント
except ImportError:
    print("japanize_matplotlib がないため日本語が文字化けする可能性があります: pip install japanize-matplotlib")

# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------
SEED = 42
DATA_FILE = Path("90_data") / "processed_poke_data_USUM.csv"

# 種族値6項目
STATS = ["HP", "攻撃", "防御", "特攻", "特防", "素早"]

# 世代の境界（全国図鑑番号の上限）。第7世代の上限809はメルタン・メルメタルを含む値で、
# USUM のデータ自体は807まで。世代ごとの図鑑番号の個数を数えるときは注意する。
GEN_BOUNDS = [0, 151, 251, 386, 493, 649, 721, 809]

# 描画色（dataviz 参照パレット・ライトモード）
# カテゴリ色は必ずこの順で使う（系列の順位で塗り替えない）。
# 散布図など全ペアが接する図では先頭3色まで。4色以上は「その他」にまとめるか分割表示する。
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
           "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SEQ_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "poke_seq", ["#cde2fb", "#86b6ef", "#2a78d6", "#1c5cab", "#0d366b"])
DIV_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "poke_div", ["#2a78d6", "#f0efec", "#e34948"])
INK = {"primary": "#0b0b0b", "secondary": "#52514e", "muted": "#898781",
       "grid": "#e1e0d9", "axis": "#c3c2b7", "surface": "#fcfcfb"}


# ---------------------------------------------------------------------------
# 乱数・描画設定
# ---------------------------------------------------------------------------
def get_rng(seed=SEED):
    """再現性のある乱数生成器を返す."""
    return np.random.default_rng(seed)


def setup_plot():
    """matplotlib の共通スタイル（細いマーク・控えめな軸とグリッド）."""
    mpl.rcParams.update({
        # IPAexGothic にない記号（≥ ≤ ₁ ᵀ など）は DejaVu Sans で補う（matplotlib 3.6 以降の字形単位フォールバック）
        "font.family": [mpl.rcParams["font.family"][0], "DejaVu Sans"],
        "figure.figsize": (7, 4.5),
        "figure.dpi": 100,
        "figure.facecolor": INK["surface"],
        "axes.facecolor": INK["surface"],
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
        "axes.edgecolor": INK["axis"],
        "axes.labelcolor": INK["secondary"],
        "axes.titlecolor": INK["primary"],
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": INK["grid"],
        "grid.linewidth": 0.6,
        "xtick.color": INK["muted"],
        "ytick.color": INK["muted"],
        "xtick.labelcolor": INK["secondary"],
        "ytick.labelcolor": INK["secondary"],
        "lines.linewidth": 2,
        "lines.markersize": 6,
        "patch.edgecolor": INK["surface"],   # 隣接する棒の間に地色の隙間
        "patch.linewidth": 1,
        "legend.frameon": False,
        "legend.labelcolor": INK["secondary"],
        "image.cmap": "poke_seq",
    })
    mpl.colormaps.register(SEQ_CMAP, force=True)
    mpl.colormaps.register(DIV_CMAP, force=True)


# ---------------------------------------------------------------------------
# データ読込・前処理
# ---------------------------------------------------------------------------
def find_data_path():
    """CSV の場所を探す.

    環境変数 POKE_DATA → このファイルの親ディレクトリ → カレントディレクトリの親、の順に
    ``90_data/processed_poke_data_USUM.csv`` を探す。
    """
    env = os.environ.get("POKE_DATA")
    if env:
        return Path(env)
    starts = [Path.cwd().resolve()]
    if "__file__" in globals():
        starts.insert(0, Path(__file__).resolve().parent)
    for start in starts:
        for d in [start, *start.parents]:
            if (d / DATA_FILE).exists():
                return d / DATA_FILE
    raise FileNotFoundError(f"{DATA_FILE} が見つかりません。環境変数 POKE_DATA でパスを指定してください。")


def _ev_total(s):
    """努力値の文字列（例: '特攻+1\\n特防+1'）から合計ポイントを求める."""
    return sum(int(v) for v in re.findall(r"\+(\d+)", str(s)))



def load_data(exclude_mega=False):
    """前処理済みの DataFrame を返す.

    姿違い（メガシンカ・リージョンフォーム・フォルム違い）はすべて別のポケモンとして扱う。
    ``exclude_mega=True`` のときだけメガシンカ・ゲンシカイキの行を除く。

    追加する列:
        図鑑番号     : № の枝番を除いた整数
        世代         : 図鑑番号から求めた 1〜7
        is_mega      : メガシンカ・ゲンシカイキか
        is_form      : 枝番つき（姿違い）の行か
        複合タイプ   : タイプ2を持つか
        タマゴ1, タマゴ2 : タマゴグループ（2つ目がなければ NaN）
        努力値合計   : もらえる努力値の合計ポイント（1〜3）
        成長経験値   : レベル100までの必要経験値（例: 106万 → 1060000）
        log高さ, log重さ : 自然対数
    """
    df = pd.read_csv(find_data_path(), dtype={"№": str})

    # 元データの誤り: オニシズクモのタイプが「みずむし」と1列に結合されている
    bad = df["タイプ1"] == "みずむし"
    df.loc[bad, ["タイプ1", "タイプ2"]] = ["みず", "むし"]
    # 元データの誤り: アリアドスの特防が第7世代の上方修正（60→70）前の値のまま（合計種族値400と不一致）
    df.loc[df["名前"] == "アリアドス", "特防"] = 70
    assert (df[STATS].sum(axis=1) == df["合計種族値"]).all(), "種族値の和と合計種族値が一致しない行がある"

    no = df["№"].str.split("-")
    df["図鑑番号"] = no.str[0].astype(int)
    df["世代"] = pd.cut(df["図鑑番号"], GEN_BOUNDS, labels=range(1, 8)).astype(int)
    df["is_mega"] = df["名前"].str.startswith(("メガ", "ゲンシ"))
    df["is_form"] = no.str.len() > 1
    df["複合タイプ"] = df["タイプ2"].notna()

    eggs = df["タマゴ"].str.split("\n")
    df["タマゴ1"] = eggs.str[0]
    df["タマゴ2"] = eggs.str[1]

    df["努力値合計"] = df["努力値"].map(_ev_total)
    df["成長経験値"] = df["成長"].str.replace("万", "").astype(int) * 10_000
    df["log高さ"] = np.log(df["高さ"])
    df["log重さ"] = np.log(df["重さ"])

    for c in ["タイプ1", "タイプ2", "性別", "成長", "タマゴ1", "タマゴ2"]:
        df[c] = df[c].astype("category")

    if exclude_mega:
        df = df[~df["is_mega"]]
    return df.reset_index(drop=True)


def types_of(df, t):
    """タイプ1かタイプ2のどちらかが t の行を選ぶブール Series."""
    return (df["タイプ1"] == t) | (df["タイプ2"] == t)


setup_plot()
