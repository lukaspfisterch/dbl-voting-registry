import uuid

from dbl_ingress.shaping.shape import shape_input
from dbl_voting_registry.registry import VotingRegistry
from dbl_voting_registry.events import VotingEvents

def test_event_determinism():
    # Verify that the same event data produces the same digest
    admission = shape_input(
        correlation_id="corr1",
        deterministic={"proposal_id": "prop1", "user_id": "user1", "vote": "Yes"},
    )
    e1 = VotingEvents.vote_cast(admission)
    e2 = VotingEvents.vote_cast(admission)
    
    assert e1.digest() == e2.digest()
    # Optional: if dbl-core JSON serialization is canonical (sorted keys), this should match.
    assert e1.to_json() == e2.to_json()

def test_registry_determinism_with_mocked_ids(monkeypatch):
    # Mock uuid to return a sequence
    class MockUUID:
        def __init__(self, val):
            self.val = val
        def __str__(self):
            return self.val
    
    counter = 0
    def mock_uuid4():
        nonlocal counter
        counter += 1
        return MockUUID(f"00000000-0000-0000-0000-{counter:012d}")

    monkeypatch.setattr(uuid, "uuid4", mock_uuid4)

    # Run 1
    counter = 0
    reg1 = VotingRegistry()
    pid1 = reg1.submit_proposal({"text": "Prop 1"})
    reg1.check_eligibility({"user_id": "Alice", "eligible": True, "proof": {"secret": "valid_token"}})
    reg1.cast_vote({"proposal_id": pid1, "user_id": "Alice", "vote": "Yes"})
    digest1 = reg1.get_log_digest()

    # Run 2
    counter = 0
    reg2 = VotingRegistry()
    pid2 = reg2.submit_proposal({"text": "Prop 1"})
    reg2.check_eligibility({"user_id": "Alice", "eligible": True, "proof": {"secret": "valid_token"}})
    reg2.cast_vote({"proposal_id": pid2, "user_id": "Alice", "vote": "Yes"})
    digest2 = reg2.get_log_digest()

    assert pid1 == pid2
    assert digest1 == digest2
    
    # Additional rigorous checks
    assert len(reg1.v.events) == len(reg2.v.events)
    # Check that every single event digest matches in order
    assert [e.digest() for e in reg1.v.events] == [e.digest() for e in reg2.v.events]


def test_end_to_end_ingress_determinism_with_observational_noise(monkeypatch):
    class MockUUID:
        def __init__(self, val):
            self.val = val
        def __str__(self):
            return self.val

    counter = 0
    def mock_uuid4():
        nonlocal counter
        counter += 1
        return MockUUID(f"00000000-0000-0000-0000-{counter:012d}")

    monkeypatch.setattr(uuid, "uuid4", mock_uuid4)

    counter = 0
    reg1 = VotingRegistry()
    pid1 = reg1.submit_proposal({"text": "Prop 1"})
    reg1.check_eligibility({"user_id": "Alice", "eligible": True, "proof": {"meta": {"t": "12:00"}}})
    reg1.cast_vote({"proposal_id": pid1, "user_id": "Alice", "vote": "Yes"})
    digest1 = reg1.get_log_digest()

    counter = 0
    reg2 = VotingRegistry()
    pid2 = reg2.submit_proposal({"text": "Prop 1"})
    reg2.check_eligibility({"user_id": "Alice", "eligible": True, "proof": {"meta": {"t": "12:01"}}})
    reg2.cast_vote({"proposal_id": pid2, "user_id": "Alice", "vote": "Yes"})
    digest2 = reg2.get_log_digest()

    assert pid1 == pid2
    assert digest1 == digest2
