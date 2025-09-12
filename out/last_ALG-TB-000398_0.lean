import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 31 * (38 + 36) = 2294 := by
  trivial
#print axioms Proof
#check Proof