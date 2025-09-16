import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : ∀ x : ℝ, 0 ≤ (x - 3)^2 := by
  taut
#print axioms Proof
#check Proof