import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 18 + 24 = 42 := by
  trivial
#print axioms Proof
#check Proof