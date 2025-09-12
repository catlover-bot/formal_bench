import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 19 * 18 = 342 := by
  trivial
#print axioms Proof
#check Proof