# formal\_bench: A tactic-ablations benchmark for Lean 4

## TL;DR

* **目的**: Lean 4 での**タクティク族ごとの性能差**と**前処理（`intros`）の寄与**を、再現性高く測るための**合成ミクロ・ベンチ**。
* **ベンチ構成（v0\_4）**: `eq`（等式）/ `lin`（線形不等式）/ `nlin`（非線形不等式）を**各200問＝計600問**。
* **評価トラック**:

  * **Strong**（全タクティク許可） → 600/600
  * **Mid**（`nlinarith/aesop`不使用） → 400/600（eq+linのみ通過）
  * **Banned**（`--ban_strong={nlinarith,aesop}`） → 400/600
  * **No-Intros**（`intros`無し） → 0/600（量化や仮説導入が不可欠であることを実証）
* **指標**: Pass\@k・AUC\@Time・勝者タクティク分布・style別パス率。

> 既存ベンチ（LeanDojo/miniF2F等）が「実在定理・検索/前提選択・高難度総合」の評価に重心があるのに対し、本ベンチは**リング/線形/非線形タクティクの“対応関係”を制御**し、**禁止/前処理アブレーション**で差分を**定量**する点が新規。
> Goedel-Prover など **Lean 4 直接証明モデル**の評価に適しています。([arXiv][1])

---

## 1. セットアップ

```bash
git clone <this_repo> formal_bench
cd formal_bench
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt    # jinja2 など
# Lean4 + Mathlib 環境（elan/lake）を用意。lean/ 下のプロジェクトを lake build
```

* **Lean4 + Mathlib 必須**（テンプレは `import Mathlib` 前提）。
* macOS/Linux 想定。Windows は WSL を推奨。

---

## 2. ベンチの中身

* 生成スクリプト: `tools/make_hard_mix_v2.py`

  * `eq`: 例 `∀ x y : ℚ, (x + y)^2 = x^2 + 2*x*y + y^2` → **`ring(_nf)`** が本命
  * `lin`: 例 `∀ x y : ℚ, x ≤ y ∧ y ≤ x → x = y` → **`linarith`** が本命
  * `nlin`: 例 `∀ x : ℝ, 0 ≤ (x - 3)^2` → **`nlinarith`** が本命
* 生成＆固定（v0\_4）:

```bash
python tools/make_hard_mix_v2.py data/hard_mix_v2.jsonl
cp data/hard_mix_v2.jsonl data/bench_v0_4.jsonl
```

---

## 3. 採点（grader）

* **入力**: `data/bench_*.jsonl`（1行1問、`{"id", "lean_prop", ...}`）
* **予測フォーマット (`preds/*.json`)**:


  各要素はテンプレの `by` 直下に**そのまま差し込む**タクティク列（複合OK, 例: `intros; simp [pow_two] at *; ring_nf`）。
* **実行**:

```bash
python tools/grade.py \
  --input data/bench_v0_4.jsonl \
  --preds preds/<your_preds>.json \
  --out out/<report>.json \
  --k <topk> --lean-dir lean --tpl tools/wrap_by.lean.j2 --aucT 90
# --ban_strong で {nlinarith, aesop} を禁止（本リポで修正済み）
```

* **メトリクス**: `Pass@k`, `QES`, `AUC@Time` と、各問題の `winner`（勝者タクティク）。

---

## 4. 既定ベースラインと再現結果（v0\_4）

| Track     | Pass\@k | 備考                                                                  |
| --------- | ------: | ------------------------------------------------------------------- |
| Strong    |  100.0% | 勝者は `intros; nlinarith` が主                                          |
| Mid       |   66.7% | `eq` は `intros; simp [pow_two]; ring_nf`、`lin` は `intros; linarith` |
| Banned    |   66.7% | `--ban_strong={nlinarith,aesop}`                                    |
| No-Intros |    0.0% | 量化/仮説導入ができず全滅                                                       |

* **style×track**（v0\_4, 200問ずつ）

  * Strong: `eq 100% / lin 100% / nlin 100%`
  * Mid/Banned: `eq 100% / lin 100% / nlin 0%`
  * No-Intros: `eq/lin/nlin 全て 0%`

---

## 5. 主要モデルを流す（Goedel-Prover / DeepSeek-Prover など）

### 5.1 予測ファイルの共通仕様

* **入力**: `data/bench_v0_4.jsonl`
* **出力**: `preds/<model>.json`（`{id: [cand1, cand2, ...]}`）

  * `cand` は **`by` 直後に貼るタクティク列**（複数行OK）。
  * 例（マルチライン）:

    ```
    intros
    simp [pow_two] at *
    ring_nf
    ```

### 5.2 Goedel-Prover を流す

* モデル配布: Goedel-Prover / Goedel-Prover-V2（8B/32B; Hugging Face）([GitHub][2])
* 概要/論文: プロジェクトサイト・arXiv/COLM 2025。([Goedel-Prover][3])

**最小アダプタ例（Transformers）**

```bash
# adapters/goedel/gen_preds.py を作成して実行
python adapters/goedel/gen_preds.py \
  --bench data/bench_v0_4.jsonl \
  --out preds/goedel_v2_8b.json \
  --model Goedel-LM/Goedel-Prover-V2-8B \
  --k 8 --temperature 0.6 --max-new-tokens 512
```

````python
# adapters/goedel/gen_preds.py（要 transformers, accelerate）
import json, argparse, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROMPT = """You are a Lean 4 prover. Fill only the proof body after `by` for the following theorem; do not print the statement again.

example : {prop} := by
"""

def clean(s: str) -> str:
    s = s.strip().strip("`").strip()
    for fence in ("```lean", "```", "LEAN>"):
        s = s.replace(fence, "")
    return s.strip()

def main(a):
    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
    mdl = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True)
    preds = {}
    for line in open(a.bench, encoding="utf-8"):
        ex = json.loads(line); pid, prop = ex["id"], ex["lean_prop"]
        cands=[]
        for _ in range(a.k):
            prompt = PROMPT.format(prop=prop)
            out = mdl.generate(**tok(prompt, return_tensors="pt").to(mdl.device),
                               do_sample=True, temperature=a.temperature,
                               max_new_tokens=a.max_new_tokens)
            text = tok.decode(out[0], skip_special_tokens=True).split("by",1)[-1]
            cands.append(clean(text))
        preds[pid]=cands
    with open(a.out,"w",encoding="utf-8") as f: f.write(json.dumps(preds, ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--bench", required=True); p.add_argument("--out", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--k", type=int, default=8)
    p.add_argument("--temperature", type=float, default=0.6)
    p.add_argument("--max-new-tokens", type=int, default=512)
    main(p.parse_args())
````

**採点**

```bash
python tools/grade.py \
  --input data/bench_v0_4.jsonl \
  --preds preds/goedel_v2_8b.json \
  --out out/goedel_v2_8b_v0_4.json \
  --k 8 --lean-dir lean --tpl tools/wrap_by.lean.j2 --aucT 90
```

> 参考: Goedel-Prover は Lean4 での SOTA 系 LLM。V2 の 8B/32B モデルが公開済み。([Hugging Face][4])

### 5.3 DeepSeek-Prover を流す

* リポジトリ/モデル: V1.5 / V2 が公開（Lean4 向け）。([GitHub][5])
* 使い方は上のアダプタと同様に**出力を「by 直下の証明本体」に正規化**して `preds/*.json` を作成。

---

## 6. 便利オプション・高速化

* `--ban_strong` : 既定で **{`nlinarith`, `aesop`}** を禁止（本リポで修正済み）。
* 並列化/タイムアウト: `grade.py` に `--jobs N` / `--timeout SEC` を用意（未設定なら実装推奨）。
* **先勝ち打ち切り**: 候補が通ったら残りを打ち切って時間短縮。

---

## 7. 再現スクリプト（一括）

```bash
# 1) ベンチ生成
python tools/make_hard_mix_v2.py data/hard_mix_v2.jsonl
cp data/hard_mix_v2.jsonl data/bench_v0_4.jsonl

# 2) 既定ベースライン（Strong/Mid/Banned/No-Intros）
#   それぞれの preds を作って grade.py を回す（examples/preds に雛形あり）

# 3) まとめ
python scripts/summarize_results.py  # out/*.json → out/*.csv 図表
```

---

## 8. 既知の制約・拡張予定

* **合成ミクロ問題**中心：実在定理/前提選択/長い証跡の難しさは直接は測らない。
* 今後: 変数数・次数で難度パラメトリック化、`have` 必須、絶対値/交差項の nlin 強化、LLM 生成タクティク混合の探索など。
* **安全検証**を強化したい場合は SafeVerify などの外部チェッカを併用可。([GitHub][6])

---

## 9. 関連・参考

* **Goedel-Prover**（サイト/論文/コード/モデル）: SOTA を報告する Lean4 向け LLM。([Goedel-Prover][3])
* **DeepSeek-Prover**（V1.5/V2）: Lean4 向け open-source 系列。([GitHub][5])

---

## 10. 引用

このベンチを利用する場合は、当リポジトリ（formal\_bench）と併せ、比較対象として以下のモデル/研究を引用してください：

* Goedel-Prover（COLM 2025）([arXiv][1])
* Goedel-Prover-V2 モデルカード（HF）([Hugging Face][4])
* DeepSeek-Prover（V1.5/V2）([GitHub][5])

---

### 付録: `preds/*.json` の最小例

```json
{
  "hard_ring_eq_0": ["intros; simp [pow_two] at *; ring_nf", "ring_nf"],
  "hard_linarith_0": ["intros; linarith", "linarith"],
  "hard_nlin_0": ["intros; nlinarith"]
}
```

---

必要なら、`adapters/` 以下をこちらで雛形コミット用に切って渡します（Goedel/DeepSeek 共通）。

[1]: https://arxiv.org/html/2502.07640v3?utm_source=chatgpt.com "A Frontier Model for Open-Source Automated Theorem Proving - arXiv"
[2]: https://github.com/Goedel-LM/Goedel-Prover?utm_source=chatgpt.com "Goedel-LM/Goedel-Prover"
[3]: https://goedel-lm.github.io/?utm_source=chatgpt.com "Goedel-Prover"
[4]: https://huggingface.co/Goedel-LM/Goedel-Prover-V2-8B?utm_source=chatgpt.com "Goedel-LM/Goedel-Prover-V2-8B"
[5]: https://github.com/deepseek-ai/DeepSeek-Prover-V1.5?utm_source=chatgpt.com "deepseek-ai/DeepSeek-Prover-V1.5"
[6]: https://github.com/GasStationManager/SafeVerify?utm_source=chatgpt.com "GasStationManager/SafeVerify: A Lean4 script for robustly ..."



