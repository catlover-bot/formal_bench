import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 8 6 = 28 := by
  ring
#print axioms Proof
#check Proof