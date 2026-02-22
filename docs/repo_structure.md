# リポジトリ構成メモ

このファイルは、初めて見る人向けの案内です。

## 読み始める順番

1. `README.md`
2. `benchmarks/bench_v0_4.meta.json`
3. `benchmarks/bench_v0_4.jsonl`
4. `scripts/README.md`
5. `scripts/run_lean_eval.py`
6. `results/<run-id>/final_table.csv`

## 各ディレクトリの役割

- `benchmarks/` : 発表で使うベンチマーク本体（JSONL + meta）
- `data/` : ベンチ作成・検証の途中で作った派生データ
- `preds/` : モデル予測（JSON）
- `results/` : 集計済み CSV（表の元データ）
- `out/` : 実行時の中間ファイル、レポート、図
- `scripts/` : 評価・正規化・集計の実行スクリプト
- `tools/` : データ生成・検査の補助ツール
- `lean/` : Lean / Lake / mathlib 実行環境
- `parts/`, `parts_ok/`, `parts_ng/` : 分割データと判定結果

次は中身を消さない前提で扱ってください。

- `benchmarks/`
- `data/`
- `preds/`
- `results/`
- `out/`
- `parts/`
- `parts_ok/`
- `parts_ng/`

## スクリプトの入口

- `scripts/run_lean_eval.py`
- `scripts/normalize_pred_heads.py`
- `scripts/normalize_pred_heads_with_style.py`
- `scripts/summarize_head_match.py`

既存名も残してあるので、古い実験メモのコマンドはそのまま使えます。
