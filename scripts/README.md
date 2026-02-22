# scripts

よく使うスクリプトの入口を、短く分かりやすい名前でも呼べるようにしています。

## 追加した入口（推奨）

- `run_lean_eval.py` : Lean 4 で評価（chunk 実行）
- `normalize_pred_heads.py` : 予測の先頭タクティクを正規化
- `normalize_pred_heads_with_style.py` : `style` を使ったフォールバック付き正規化
- `summarize_head_match.py` : 先頭タクティク一致率の集計

## 既存名（互換のため残す）

- `eval_success_lean4_chunked.py`
- `canonize_pred.py`
- `canonize_pred_with_style.py`
- `summarize_runs.py`

## 補足

新しい入口は、既存スクリプトを呼び出すだけの薄いラッパーです。
