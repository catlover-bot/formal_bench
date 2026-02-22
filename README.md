# formal_bench

Lean 4 のタクティク生成を評価するためのデータ、予測結果、評価スクリプト、集計結果をまとめています。

提案手法の流れは次の 3 段です。

`Gate -> style-canon -> Lean 実行`

## 最初に見るファイル

- `README.md` : 全体の説明（このファイル）
- `docs/repo_structure.md` : ディレクトリ構成の説明
- `benchmarks/bench_v0_4.meta.json` : ベンチの件数とハッシュ
- `scripts/README.md` : スクリプト一覧

## データセット

- 本体: `benchmarks/bench_v0_4.jsonl`
- メタ情報: `benchmarks/bench_v0_4.meta.json`
- 件数: `600`
- SHA-256: `c054cf5f3db2af6f2c1b8c8e62b05e7e7ca5d2f2202857eb037a6e65aa862f4f`

## 大事な方針

このリポジトリには、実験の途中生成物や発表確認に使うファイルが多く入っています。次のディレクトリは、整理のために中身を消さないでください。

- `benchmarks/`
- `data/`
- `preds/`
- `results/`
- `out/`
- `parts/`
- `parts_ok/`
- `parts_ng/`

## ディレクトリの見方

- `benchmarks/` : 実験で使用したデータセット
- `data/` : 作成途中・検証途中の JSONL
- `preds/` : モデル出力（予測）
- `results/` : 集計済みの CSV
- `out/` : 実行時の中間生成物、ログ、図
- `scripts/` : 評価・正規化・集計スクリプト
- `tools/` : ベンチ作成や検査用のツール
- `lean/` : Lean / Lake の実行環境
- `parts*` : 合成データ作成時の分割ファイルと判定結果

## よく使うスクリプト

分かりやすい名前の入口を追加しています。既存の古い名前も残してあるので、以前のメモやコマンドはそのまま使えます。

- Lean で評価する: `scripts/run_lean_eval.py`
- 予測ヘッドを正規化する: `scripts/normalize_pred_heads.py`
- style 情報付きで正規化する: `scripts/normalize_pred_heads_with_style.py`
- 先頭タクティク一致率を集計する: `scripts/summarize_head_match.py`

## 使い方（例）

前提:

- `lean/` で Lean / Lake / mathlib が動く
- Python 環境を `environment.yml` または `requirements.txt` で作る

```bash
conda env create -f environment.yml
conda activate formal-bench
```

```bash
python scripts/run_lean_eval.py \
  --bench benchmarks/bench_v0_4.jsonl \
  --preds preds/sample_preds.json \
  --workdir lean \
  --batch 100 \
  --timeout 1200
```

## 提案手法

- `Gate` : 出力を一行タクティク列に寄せる前処理
- `style-canon` : 表記ゆれの正規化
- `Lean 実行` : 最終的な正否判定

詳しいディレクトリ説明は `docs/repo_structure.md` を見てください。
