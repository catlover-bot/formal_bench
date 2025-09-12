import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 27 * (33 + 37) = 1890 := by
  trivial
#print axioms Proof
#check Proof