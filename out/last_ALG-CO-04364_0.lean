import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 21 * (31 + 10) = 861 := by
  trivial
#print axioms Proof
#check Proof