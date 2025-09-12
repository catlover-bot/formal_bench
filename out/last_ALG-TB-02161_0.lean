import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 38 * (10 + 22) = 1216 := by
  trivial
#print axioms Proof
#check Proof