import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 24 + 0 + 23 = 47 := by
  trivial
#print axioms Proof
#check Proof