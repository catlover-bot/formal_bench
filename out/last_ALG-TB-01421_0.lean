import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 27 + 3 + 20 = 50 := by
  trivial
#print axioms Proof
#check Proof