import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.gcd 60 28 = 4 := by
  trivial
#print axioms Proof
#check Proof