import Mathlib
import Aesop
import Std.Tactic
set_option linter.docPrime false
set_option maxHeartbeats 400000

theorem Proof : Nat.gcd 6 24 = 6 := by
  trivial
#print axioms Proof
#check Proof