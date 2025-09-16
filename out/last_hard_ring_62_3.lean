import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : ∀ x y : ℤ, (x + y + 2)^2 = (x + y + 2)*(x + y + 2) := by
  norm_num
#print axioms Proof
#check Proof