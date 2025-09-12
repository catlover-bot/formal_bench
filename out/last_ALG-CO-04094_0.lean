import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : 23 * (36 + 6) = 966 := by
  trivial
#print axioms Proof
#check Proof