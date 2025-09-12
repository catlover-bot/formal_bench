import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 39 * 17 = 663 := by
  trivial
#print axioms Proof
#check Proof