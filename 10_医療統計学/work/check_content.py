"""改訂後の内容を自動検査する（ビルド前でも実行可）．問題があれば非0で終了．

検査項目:
  1. 参照：未定義ラベルへの \\cref/\\ref と，削除した章（ch11, ch15）のラベルへの依存
  2. 章番号の直書き（「第9章」など．『現代数理統計学の基礎』など他書の章は除く）
  3. 削除した概念の残存（付録F・exambox・許可した節を除く）
  4. 発展項目の不整合：発展ブロックで導入した手法名が goal・手法選択・まとめ・付録A に出ていないか
使い方: python check_content.py
"""
import pathlib
import re
import sys

from build import ORDER, PARTS

sys.stdout.reconfigure(encoding="utf-8")

texts = {name: (PARTS / name).read_text(encoding="utf-8") for name in ORDER}


def strip_comments(s: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", s)


def lines_of(name):
    for i, line in enumerate(strip_comments(texts[name]).splitlines(), 1):
        yield i, line


problems = []


def report(kind, name, line, msg):
    problems.append(f"[{kind}] {name}:{line}: {msg}")


# ---------- 1. 参照 ----------
labels = set()
for name, s in texts.items():
    labels |= set(re.findall(r"\\label(?:\[[^\]]*\])?\{([^}]+)\}", strip_comments(s)))
REF = re.compile(r"\\(?:[cC]ref|ref|eqref|pageref|autoref|labelcref)\{([^}]+)\}")
DELETED_PREFIX = re.compile(r"^(?:ch:(?:11|15)$|[a-z]+:(?:11|15)-)")
for name in ORDER:
    for i, line in lines_of(name):
        for group in REF.findall(line):
            for lab in (x.strip() for x in group.split(",")):
                if "#" in lab:  # マクロ定義内の引数
                    continue
                if DELETED_PREFIX.match(lab):
                    report("ref", name, i, f"削除した章のラベル {lab}")
                elif lab not in labels:
                    report("ref", name, i, f"未定義ラベル {lab}")

# ---------- 2. 章番号の直書き ----------
OTHER_BOOK = re.compile(r"同書|現代数理統計学|教科書|久保川|基礎』|文献|\\cite")
CHAP = re.compile(r"第\s*[0-9０-９]+\s*章|(?<![0-9.．])[0-9]+\s*章(?!末)")
for name in ORDER:
    if name == "00_preamble.tex":  # \crefname の書式定義
        continue
    for i, line in lines_of(name):
        if CHAP.search(line) and not OTHER_BOOK.search(line):
            report("chapnum", name, i, f"章番号の直書き: {CHAP.search(line).group(0)}")

# ---------- 3. 削除した概念の残存 ----------
DELETED_TERMS = [
    "DeLong", "MMRM", "GEE", "一般化線形混合", "RMST", "Nelson", "Aalen", "Gray 検定", "Gray の検定",
    "Simon", "Simes", "Dunnett", "Hommel", "MCP-Mod", "Rubin のルール", "Rubin の規則", "傾向スコア", "直接標準化",
    "DerSimonian", "TOST", "Peto", "Lord", "Slepian", "Hauck", "Firth", "Hosmer",
    "log-二項", "修正ポアソン", "条件付きロジスティック", "メタアナリシス", "Toeplitz", "Šidák", "Sidak",
    "平均への回帰", "鏡像原理",
]
# 付録F（誘導付き概念の一覧）と exambox の中は許可
ALLOWED_ENV = re.compile(r"\\begin\{exambox\}.*?\\end\{exambox\}", re.S)


def masked(name):
    s = strip_comments(texts[name])
    s = ALLOWED_ENV.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), s)
    if name == "90_appendix.tex":
        # 付録D（過去問対応表）と付録F（誘導付き概念の一覧）は出題内容の記述なので許可
        for app in ("D", "F"):
            m = re.search(r"\\label(?:\[[^\]]*\])?\{app:" + app + r"\}", s)
            if m:
                start = s.rfind("\\chapter", 0, m.start())
                end = s.find("\\chapter", m.end())
                end = len(s) if end < 0 else end
                s = s[:start] + re.sub(r"[^\n]", " ", s[start:end]) + s[end:]
    return s


for name in ORDER:
    # 文献の題名と，前付（扱う範囲の説明・出題分析）は対象外
    if name in ("99_bib.tex", "01_front.tex"):
        continue
    for i, line in enumerate(masked(name).splitlines(), 1):
        for t in DELETED_TERMS:
            if t in line:
                report("deleted", name, i, f"削除した概念 '{t}'")

# ---------- 4. 発展項目の不整合 ----------
def blocks(s, start_pat, end_pat):
    for m in re.finditer(start_pat, s):
        e = re.compile(end_pat).search(s, m.end())
        yield s[m.start(): e.end() if e else len(s)]


def hatten_blocks(s):
    out = list(blocks(s, r"\\begin\{supbox\}\[発展", r"\\end\{supbox\}"))
    for m in re.finditer(r"\\Hatten", s):
        line_start = s.rfind("\n", 0, m.start()) + 1
        line = s[line_start: s.find("\n", m.end())]
        if re.match(r"\s*\\(sub)*section", line):
            e = re.compile(r"\\(?:sub)?section|\\chapter").search(s, m.end())
        else:
            e = re.compile(r"\n\s*\n").search(s, m.end())
        out.append(s[line_start: e.start() if e else len(s)])
    return out


TOKEN = re.compile(r"\b[A-Z][A-Za-z]+(?:--[A-Z][A-Za-z]+)*\b")
COMMON = {"Cox", "Wald", "Fisher", "Bayes", "Bernoulli", "Poisson", "Brown", "AIC", "OR", "RR", "HR",
          "CI", "MLE", "ROC", "AUC", "PPV", "NPV", "Kaplan--Meier", "Mann--Whitney", "Wilcoxon",
          "Bonferroni", "Holm", "McNemar", "Mantel--Haenszel", "Cochran", "Pearson", "Student", "Weibull",
          "Newton", "Slutsky", "EM", "Beta", "Gamma", "Normal", "The", "A", "B"}
GOAL_LIKE = [r"\\begin\{goalbox\}", r"\\begin\{summarybox\}", r"\\label\{sec:\d+-choice\}"]

for name in ORDER:
    s = strip_comments(texts[name])
    hb = hatten_blocks(s)
    if not hb:
        continue
    hatten_text = "".join(hb)
    rest = s
    for b in hb:
        rest = rest.replace(b, "")
    names = {t for t in TOKEN.findall(hatten_text)} - COMMON
    goal_parts = []
    goal_parts += list(blocks(s, r"\\begin\{goalbox\}", r"\\end\{goalbox\}"))
    goal_parts += list(blocks(s, r"\\begin\{summarybox\}", r"\\end\{summarybox\}"))
    goal_parts += list(blocks(s, r"\\section\{[^}]*\}\\label\{sec:\d+-choice\}", r"\\section|\\chapter"))
    goal_text = "".join(goal_parts)
    for t in sorted(names):
        if t in goal_text:
            report("hatten", name, 0, f"発展で導入した '{t}' が goal/手法選択/まとめ に出ている")
    for t in sorted(names):
        appA = "".join(blocks(texts["90_appendix.tex"], r"\\label(?:\[[^\]]*\])?\{app:A\}", r"\\chapter"))
        if t in appA:
            report("hatten", "90_appendix.tex", 0, f"{name} の発展 '{t}' が付録Aに出ている")

# ---------- 5. PDF に LaTeX コマンド名が漏れていないか（ビルド後のみ） ----------
pdf = PARTS.parent / "build" / "医療統計学参考書.pdf"
if pdf.exists():
    import fitz
    LEAK = re.compile(r"(?<![A-Za-z])(mbox|cref|textbf|frac|mathbf|kakomon|Hissu|Hinshutsu|Youchui|Hatten"
                      r"|begin|label|times|alpha|beta)(?![A-Za-z])")
    for i, page in enumerate(fitz.open(pdf), 1):
        t = page.get_text()
        for m in LEAK.finditer(t):
            ctx = t[max(0, m.start() - 15): m.end() + 15].replace("\n", " ")
            if "alpha spending" in ctx:  # 用語集の英語表記
                continue
            report("leak", "PDF", i, f"コマンド名 '{m.group(1)}' が表示されている: {ctx}")

for p in problems:
    print(p)
print(f"--- {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
