import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 4 2 = 6 := by
  linarith
#print axioms Proof
#check Proof