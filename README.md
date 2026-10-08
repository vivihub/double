# Double

ホリプロデジタルエンターテインメント「Double」関連の公開ページ。

| パス | 内容 |
|---|---|
| `index.html` | Double ロードマップ（10,000人規模コミュニティ構想） |
| `kpi/` | **所属クリエイター KPI 予実ダッシュボード**（GitHub Pages: `/double/kpi/`） |
| `artifact/` | 同ダッシュボードの claude.ai Artifact 用ビルド |
| `src/` | ダッシュボードのテンプレート（head / body） |
| `data/` | 取得済みの生データ（Google Sheets / Notion）。備考欄は除外 |
| `scripts/build.py` | `data/` → `kpi/`・`artifact/` を生成 |

## KPI ダッシュボードの更新手順（デイリー）

1. Google Sheets「【Double】リストアップシート」から次の範囲を取得し `data/` に保存
   - `2026年度進捗管理!A1:F25` → `data/sheet_progress.json`
   - `Double!A1:T` → `data/sheet_double.json`（**S列「備考」は削除してから保存**。住所・電話が含まれるため）
   - `レーベル!A1:H` → `data/sheet_label.json`
2. Notion「目標・Action Plan」の月次表が更新されていれば `data/notion_monthly.json` を更新
3. `python3 scripts/build.py`
4. `git commit` → `git push`、`artifact/index.html` を Artifact へ再公開

この手順は Claude のスケジュールタスクで毎朝自動実行される。
