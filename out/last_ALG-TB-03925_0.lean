import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 38 + 39 + 30 = 107 := by
  trivial
#print axioms Proof
#check Proof