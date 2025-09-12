import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.choose 5 3 = 10 := by
  ring
#print axioms Proof
#check Proof