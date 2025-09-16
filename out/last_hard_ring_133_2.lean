import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : ∀ x y : ℤ, (x + y + 0)^2 = (x + y + 0)*(x + y + 0) := by
  nlinarith
#print axioms Proof
#check Proof