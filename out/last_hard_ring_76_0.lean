import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : ∀ x y : ℤ, (x + y + -3)^2 = (x + y + -3)*(x + y + -3) := by
  intros; linarith
#print axioms Proof
#check Proof