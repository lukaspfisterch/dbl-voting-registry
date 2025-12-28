from typing import Dict, Set, Optional
import uuid
from dbl_core.behavior.log import BehaviorV
from dbl_voting_registry.events import VotingEvents

class VotingRegistry:
    def __init__(self):
        self.v = BehaviorV()
        # In-memory projection of state for validation
        self._proposals: Set[str] = set()
        self._eligible_users: Set[str] = set()
        self._votes: Dict[str, Dict[str, str]] = {} # proposal_id -> {user_id -> vote}
        self._certified_results: Set[str] = set()

    def _append(self, event):
        # Update immutable V
        # BehaviorV is a frozen dataclass with a tuple of events
        new_events = self.v.events + (event,)
        self.v = BehaviorV(events=new_events)
        self._apply_event(event)
        return event

    def _apply_event(self, event):
        # Update projection
        data = event.data
        # data might be frozen (Mapping), handle generic access
        
        etype = data.get("type")

        if etype == "PROPOSAL_SUBMITTED":
            self._proposals.add(data["proposal_id"])
            self._votes[data["proposal_id"]] = {}
        
        elif etype == "ELIGIBILITY_CHECKED":
            # Observational only. Does NOT affect state.
            pass
        
        elif etype == "VOTER_ADMITTED":
            # Normative Decision. Updates state.
            self._eligible_users.add(data["user_id"])
        
        elif etype == "VOTE_CAST":
            pid = data["proposal_id"]
            uid = data["user_id"]
            vote = data["vote"]
            if pid in self._votes:
                self._votes[pid][uid] = vote

        elif etype == "RESULT_CERTIFIED":
            self._certified_results.add(data["proposal_id"])

    def submit_proposal(self, text: str) -> str:
        pid = str(uuid.uuid4())
        base_id = str(uuid.uuid4()) # Correlation for this flow
        event = VotingEvents.proposal_submitted(base_id, pid, text)
        self._append(event)
        return pid

    def check_eligibility(self, user_id: str, proof: dict) -> bool:
        # Simulate external check logic.
        is_valid = proof.get("secret") == "valid_token"
        
        # 1. Emit Observational Proof (Records that we checked, and what we saw)
        proof_id = str(uuid.uuid4())
        proof_event = VotingEvents.eligibility_checked(proof_id, user_id, proof_data=proof)
        self._append(proof_event)
        
        if is_valid:
            # 2. Emit Normative Decision (If check passed)
            decision_id = str(uuid.uuid4())
            decision_event = VotingEvents.voter_admitted(decision_id, user_id)
            self._append(decision_event)
            return True
        else:
            return False

    def cast_vote(self, proposal_id: str, user_id: str, vote: str) -> bool:
        # 1. Check constraints (Boundary logic)
        if proposal_id not in self._proposals:
            raise ValueError("Unknown proposal")
        if user_id not in self._eligible_users:
            raise ValueError("User not eligible (must pass check_eligibility first)")
        if proposal_id in self._certified_results:
            raise ValueError("Voting closed")

        base_id = str(uuid.uuid4())
        event = VotingEvents.vote_cast(base_id, proposal_id, user_id, vote)
        self._append(event)
        return True

    def certify_result(self, proposal_id: str) -> dict:
        if proposal_id not in self._proposals:
            raise ValueError("Unknown proposal")
        
        # Calculate tally from projection
        votes = self._votes.get(proposal_id, {})
        tally = {"Yes": 0, "No": 0}
        for v in votes.values():
            if v in tally:
                tally[v] += 1
            else:
                tally[v] = tally.get(v, 0) + 1
        
        base_id = str(uuid.uuid4())
        event = VotingEvents.result_certified(base_id, proposal_id, tally)
        self._append(event)
        return tally

    def get_log_digest(self) -> str:
        return self.v.digest()
