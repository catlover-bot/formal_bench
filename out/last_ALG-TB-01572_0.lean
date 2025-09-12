import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 32 + 3 + 36 = 71 := by
  trivial
#print axioms Proof
#check Proof