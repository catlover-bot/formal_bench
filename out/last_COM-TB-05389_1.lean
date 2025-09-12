import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 8 3 = 56 := by
  ring
#print axioms Proof
#check Proof