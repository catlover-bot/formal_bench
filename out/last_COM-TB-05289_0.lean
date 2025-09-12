import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 5 2 = 10 := by
  trivial
#print axioms Proof
#check Proof