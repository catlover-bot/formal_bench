import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 4 3 = 4 := by
  trivial
#print axioms Proof
#check Proof