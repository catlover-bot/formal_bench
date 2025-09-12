import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 12 * (0 + 34) = 408 := by
  trivial
#print axioms Proof
#check Proof