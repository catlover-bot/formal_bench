import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : ∀ x y : ℤ, (x + y + 4)^2 = (x + y + 4)*(x + y + 4) := by
  aesop
#print axioms Proof
#check Proof