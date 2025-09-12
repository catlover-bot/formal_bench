import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 35 + 14 + 8 = 57 := by
  trivial
#print axioms Proof
#check Proof