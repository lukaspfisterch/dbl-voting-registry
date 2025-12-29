import sys
import os

# Ensure we can import from src and dbl-core-dev
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
# Assuming dbl-core-dev is at ../dbl-core-dev
sys.path.append(os.path.join(os.path.dirname(__file__), "../dbl-core-dev/src"))
# Assuming kl-kernel-logic-dev is at ../kl-kernel-logic-dev
sys.path.append(os.path.join(os.path.dirname(__file__), "../kl-kernel-logic-dev/src"))

from dbl_voting_registry.registry import VotingRegistry

def main():
    print("Initializing Voting Registry...")
    registry = VotingRegistry()

    # 1. Submit Proposal
    print("\n[Step 1] Submitting Proposal")
    pid = registry.submit_proposal({"text": "Should we adopt DBL for all governance?"})
    print(f"Proposal ID: {pid}")

    # 2. Eligibility Checks
    print("\n[Step 2] Checking Eligibility")
    users = ["Alice", "Bob", "Charlie", "Mallory"]
    proofs = {
        "Alice": {"secret": "valid_token", "id_card": "A123"},
        "Bob": {"secret": "valid_token", "id_card": "B456"},
        "Charlie": {"secret": "valid_token", "id_card": "C789"},
        "Mallory": {"secret": "FAKE", "id_card": "XXX"}
    }

    for user in users:
        is_valid = registry.check_eligibility(
            {"user_id": user, "eligible": proofs[user]["secret"] == "valid_token", "proof": proofs[user]}
        )
        print(f"User {user} eligible? {is_valid}")

    # 3. Cast Votes
    print("\n[Step 3] Casting Votes")
    # Alice votes Yes
    registry.cast_vote({"proposal_id": pid, "user_id": "Alice", "vote": "Yes"})
    print("Alice voted Yes")

    # Bob votes No
    registry.cast_vote({"proposal_id": pid, "user_id": "Bob", "vote": "No"})
    print("Bob voted No")
    
    # Charlie votes Yes
    registry.cast_vote({"proposal_id": pid, "user_id": "Charlie", "vote": "Yes"})
    print("Charlie voted Yes")

    # Mallory tries to vote
    try:
        registry.cast_vote({"proposal_id": pid, "user_id": "Mallory", "vote": "Yes"})
    except ValueError as e:
        print(f"Mallory vote failed as expected: {e}")

    # 4. Certify
    print("\n[Step 4] Certifying Results")
    tally = registry.certify_result({"proposal_id": pid})
    print(f"Final Tally: {tally}")

    # 5. Digest
    print("\n[Step 5] Log Digest")
    digest = registry.get_log_digest()
    print(f"V Digest: {digest}")

    def _plain(x):
        """Recursively convert mappingproxy to dict for clean display."""
        if hasattr(x, "items"):
            return {k: _plain(v) for k, v in dict(x).items()}
        if isinstance(x, (list, tuple)):
            return [_plain(v) for v in x]
        return x

    # 6. Audit View
    print("\n[Audit View]")
    print(f"{'IDX':<4} {'KIND':<10} {'TYPE':<25} {'DATA'}")
    print("-" * 80)
    for idx, e in enumerate(registry.v.events):
        dtype = e.data.get('type', 'UNKNOWN')
        print(f"{idx:<4} {e.event_kind.name:<10} {dtype:<25}")
        print(f"     data: {_plain(e.data)}")
        if e.observational:
            print(f"     observational: {_plain(e.observational)}")

    # 7. Canonical Projection
    print("\n[Canonical Projection (Digests)]")
    for idx, e in enumerate(registry.v.events):
        print(f"{idx}: {e.digest()}")
    
    # 8. Invariance Demonstration
    print("\n[Invariance Check]")
    from dbl_ingress.admission.model import AdmissionRecord
    from dbl_voting_registry.events import VotingEvents
    adm1 = AdmissionRecord(
        correlation_id="corr_x",
        deterministic={"user_id": "UserX"},
        observational={"meta": {"t": "12:00"}},
    )
    adm2 = AdmissionRecord(
        correlation_id="corr_x",
        deterministic={"user_id": "UserX"},
        observational={"meta": {"t": "12:01"}},
    )
    p1 = VotingEvents.eligibility_checked(adm1)
    p2 = VotingEvents.eligibility_checked(adm2)
    print(f"Proof 1 Digest (t=12:00): {p1.digest()}")
    print(f"Proof 2 Digest (t=12:01): {p2.digest()}")
    print(f"Match? {p1.digest() == p2.digest()}")

    print("\nDemo Succeeded.")

if __name__ == "__main__":
    main()
