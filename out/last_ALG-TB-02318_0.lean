import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 6 + 36 + 21 = 63 := by
  trivial
#print axioms Proof
#check Proof