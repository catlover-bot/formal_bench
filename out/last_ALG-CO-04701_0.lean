import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 0 * 8 = 0 := by
  trivial
#print axioms Proof
#check Proof