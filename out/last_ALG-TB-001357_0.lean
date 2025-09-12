import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 39 * (34 + 11) = 1755 := by
  trivial
#print axioms Proof
#check Proof