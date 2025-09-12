import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 13 * (13 + 6) = 247 := by
  trivial
#print axioms Proof
#check Proof