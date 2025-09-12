import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 29 * (14 + 35) = 1421 := by
  trivial
#print axioms Proof
#check Proof