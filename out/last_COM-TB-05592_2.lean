import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 9 5 = 126 := by
  linarith
#print axioms Proof
#check Proof