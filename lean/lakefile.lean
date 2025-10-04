import Lake
open Lake DSL

package «formal-bench» where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"
  @ "stable" -- ← 既知のタグに固定できるなら置き換え（例: v4.12.0 など）
