import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 3 * (10 + 21) = 93 := by
  trivial
#print axioms Proof
#check Proof