import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 21 * (4 + 21) = 525 := by
  trivial
#print axioms Proof
#check Proof