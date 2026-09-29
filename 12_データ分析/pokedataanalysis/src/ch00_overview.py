"""第0章 データの概要（全章共通の前提）."""
from poke import *

df = load_data()

# %% 00-1
# 元の列と追加した列
cols_raw = pd.read_csv(find_data_path(), nrows=0).columns
cols_new = [c for c in df.columns if c not in cols_raw]
print(f"行数: {len(df)}  元の列: {len(cols_raw)}  追加した列: {len(cols_new)}")
print("追加した列:", cols_new)
df.head()

# %% 00-2
# 姿違いの内訳
print("枝番つき（姿違い）の行:", df["is_form"].sum())
print("  うちメガシンカ・ゲンシカイキ:", df["is_mega"].sum())
print("全国図鑑番号の種類数:", df["図鑑番号"].nunique())
print("\n世代ごとの行数")
print(df["世代"].value_counts().sort_index().to_string())

# %% 00-3
# 数値変数の要約（歪度・尖度つき）
num_cols = STATS + ["合計種族値", "高さ", "重さ", "捕獲率", "経験値", "初期なつき度", "孵化", "雄率"]
summary = df[num_cols].describe().T
summary["歪度"] = df[num_cols].skew()
summary["尖度(-3)"] = df[num_cols].kurt()
summary.round(2)

# %% 00-4
# カテゴリ変数の水準数と欠損
cat_cols = ["タイプ1", "タイプ2", "性別", "成長", "タマゴ1", "タマゴ2", "努力値合計"]
pd.DataFrame({
    "水準数": [df[c].nunique() for c in cat_cols],
    "欠損数": [df[c].isna().sum() for c in cat_cols],
    "最頻値": [df[c].mode().iloc[0] for c in cat_cols],
}, index=cat_cols)

# %% 00-5
# 重さは対数をとると歪みが小さくなる
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
axes[0].hist(df["重さ"], bins=40, color=PALETTE[0])
axes[0].set(title=f"重さ（歪度 {df['重さ'].skew():.2f}）", xlabel="重さ (kg)", ylabel="匹数")
axes[1].hist(df["log重さ"], bins=40, color=PALETTE[0])
axes[1].set(title=f"log重さ（歪度 {df['log重さ'].skew():.2f}）", xlabel="log(重さ)", ylabel="匹数")
fig.tight_layout()
plt.show()
