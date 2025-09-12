import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 29 + 19 + 5 = 53 := by
  trivial
#print axioms Proof
#check Proof