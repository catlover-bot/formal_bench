import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : ∀ x y : ℚ, x ≤ y ∧ y ≤ x → x = y := by
  linarith
#print axioms Proof
#check Proof