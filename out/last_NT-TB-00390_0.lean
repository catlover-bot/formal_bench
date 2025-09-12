import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.gcd 34 34 = 34 := by
  trivial
#print axioms Proof
#check Proof