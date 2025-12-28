
from dbl_core.behavior.log import BehaviorV
from dbl_voting_registry.events import VotingEvents
from dbl_core.events.model import DblEventKind

def test_observational_non_interference():
    """
    Verify that changing observational fields (e.g. proof details)
    does NOT change the digest of the event or the log.
    Includes nested data to stress canonicalization.
    """
    # 1. Original Event (Now PROOF kind)
    e1 = VotingEvents.eligibility_checked(
        correlation_id="corr_check",
        user_id="Alice",
        proof_data={
            "secret": "valid_token", 
            "meta": {"timestamp": "12:00", "ip": "1.1.1.1"}
        }
    )
    # A) Fix: Use Enum comparison
    assert e1.event_kind == DblEventKind.PROOF
    
    # B) Documentation Assertion: Explicitly show what is normative vs observational
    assert e1.data == {
        "type": "ELIGIBILITY_CHECKED",
        "user_id": "Alice"
    }
    assert "meta" in e1.observational["proof_details"]
    
    # 2. Modified Event (different observational data, nested change)
    e2 = VotingEvents.eligibility_checked(
        correlation_id="corr_check",
        user_id="Alice",
        proof_data={
            "secret": "valid_token", 
            "meta": {"timestamp": "12:01", "ip": "9.9.9.9"} # CHANGED
        }
    )

    # Sanity check: they are different objects with different observational data
    assert e1 != e2
    assert e1.observational != e2.observational

    # 3. Digests MUST be identical
    assert e1.digest() == e2.digest()

    # 4. Normative Data MUST be identical
    assert e1.data == e2.data

def test_normative_change_affects_digest():
    """
    Verify that changing normative fields (e.g. user_id)
    DOES change the digest.
    """
    e1 = VotingEvents.eligibility_checked(
        correlation_id="corr1",
        user_id="Alice",
        proof_data={"s": "1"}
    )
    e2 = VotingEvents.eligibility_checked(
        correlation_id="corr1",
        user_id="Bob", # CHANGED
        proof_data={"s": "1"}
    )

    assert e1.digest() != e2.digest()

def test_log_digest_invariance():
    """
    Verify that a log containing e1 vs e2 (observational diff) has same digest.
    """
    e1 = VotingEvents.eligibility_checked("c", "u", {"obs": 1})
    e2 = VotingEvents.eligibility_checked("c", "u", {"obs": 2})

    v1 = BehaviorV(events=(e1,))
    v2 = BehaviorV(events=(e2,))

    assert v1.digest() == v2.digest()
