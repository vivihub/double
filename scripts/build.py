#!/usr/bin/env python3
"""Build kpi/ (GitHub Pages) and artifact/ (claude.ai Artifact) from data/*.json.

Inputs (written by the daily refresh task):
  data/sheet_double.json    Google Sheets values of tab "Double"  (A:T, 備考 column removed)
  data/sheet_progress.json  values of tab "2026年度進捗管理" (A1:F25)
  data/sheet_label.json     values of tab "レーベル" (A1:H)
  data/notion_monthly.json  monthly table from Notion 目標・Action Plan
Run:  python3 scripts/build.py
"""
import json, collections, datetime, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"

def load(name):
    return json.load(open(D / name, encoding="utf-8"))["values"] if name.startswith("sheet") else json.load(open(D / name, encoding="utf-8"))

def fol(s):
    s = str(s).replace(",", "").strip()
    return int(s) if s.isdigit() else 0

def cell(rows, label, col=1):
    """value in the row right after the row whose column B equals label"""
    for i, r in enumerate(rows):
        if len(r) > col and r[col].strip().startswith(label):
            for nxt in rows[i + 1:i + 4]:
                if len(nxt) > col and nxt[col].strip():
                    return nxt[col]
            return ""
    return ""

# ---- progress sheet
P = load("sheet_progress.json")
target = fol(cell(P, "契約目標人数"))
total = fol(cell(P, "契約人数 総計"))
fy2026 = fol(cell(P, "2026年度 契約人数"))
cats = []
start = next(i for i, r in enumerate(P) if len(r) > 1 and r[1] == "カテゴリ")
for r in P[start + 1:]:
    if len(r) < 4 or not r[1]:
        break
    name = r[1].replace("トラベルグルメ", "トラベル・グルメ")
    cats.append({"n": name, "t": fol(r[2]), "a": fol(r[3])})

# ---- Double list
V = load("sheet_double.json")
header = V[0]
# column positions are fixed by the sheet; 備考 (orig index 18) has been removed before saving
idx = {}
for i, h in enumerate(header):
    idx.setdefault(h.replace("\n", ""), i)  # first occurrence wins (連絡者 appears twice)
def g(r, key):
    i = idx.get(key)
    return r[i] if i is not None and i < len(r) else ""
rows = [r for r in V[1:] if len(r) > 1 and r[1]]
status = collections.Counter(g(r, "ステータス") for r in rows)
genre = collections.Counter(g(r, "ジャンル") for r in rows)
PIPE = ("契約完了", "案件実施確定後 契約締結", "契約交渉中", "契約書内容確認中", "契約書送付済")
members = []
for r in rows:
    st = g(r, "ステータス")
    if st not in PIPE:
        continue
    cm = g(r, "契約完了月")
    members.append({
        "n": g(r, "アカウント名").replace("\r", "").replace("\n", " ")[:40],
        "u": g(r, "アカウント").strip(),
        "s": g(r, "SNS"), "g": g(r, "ジャンル"), "f": fol(g(r, "フォロワー数")),
        "st": st, "m": cm, "fy": "2026" if cm else "2025",
        "imp": g(r, "インパルズ登録") == "済", "pf": g(r, "成果報酬") == "〇",
        "c": (g(r, "連絡者") or g(r, "記入者")).split("\n")[0],
    })

# ---- label
L = load("sheet_label.json")
label = [{"n": r[7], "st": r[1], "d": r[2]} for r in L[1:] if len(r) > 7 and r[1] and r[1] not in ("なし！", "お断り", "アタックしない")]

data = {
    "updated": datetime.date.today().isoformat(),
    "target": target, "total": total, "fy2026": fy2026,
    "cats": cats, "monthly": load("notion_monthly.json")["monthly"],
    "status": dict(status), "genre": dict(genre), "members": members, "label": label,
}
js = "const DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
head = open(ROOT / "src/head.html", encoding="utf-8").read()
body = open(ROOT / "src/body.html", encoding="utf-8").read()

# label note is generated from data
names = "、".join(x["n"] for x in label)
body = body.replace("__LABEL_NOTE__", f"映像レーベル契約（{len(label)}名：{names}）")

(ROOT / "artifact").mkdir(exist_ok=True)
(ROOT / "artifact/index.html").write_text(head + body, encoding="utf-8")
(ROOT / "artifact/data.js").write_text(js, encoding="utf-8")
(ROOT / "kpi").mkdir(exist_ok=True)
(ROOT / "kpi/index.html").write_text(
    '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    + head + "</head>\n<body>\n" + body + "</body>\n</html>\n", encoding="utf-8")
(ROOT / "kpi/data.js").write_text(js, encoding="utf-8")
print(f"built: target={target} total={total} fy2026={fy2026} members={len(members)} rows={len(rows)}")
