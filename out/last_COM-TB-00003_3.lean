import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 6 2 = 15 := by
  nlinarith
#print axioms Proof
#check Proof