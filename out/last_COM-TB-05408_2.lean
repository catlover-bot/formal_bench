import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 7 3 = 35 := by
  linarith
#print axioms Proof
#check Proof