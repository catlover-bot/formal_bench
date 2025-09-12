import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 31 + 30 = 61 := by
  trivial
#print axioms Proof
#check Proof