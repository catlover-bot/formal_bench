import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : ∀ x : ℝ, (x - 3)^2 ≥ 0 := by
  intros; ring
#print axioms Proof
#check Proof