from typing import Dict, Mapping, Set
import uuid
from dbl_core.behavior.log import BehaviorV
from dbl_core.events.model import DblEventKind
from dbl_voting_registry.events import VotingEvents
from dbl_ingress.shaping.shape import shape_input
from dbl_ingress.admission.model import AdmissionRecord

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
        if event.event_kind != DblEventKind.DECISION:
            return
        data = event.data
        # data might be frozen (Mapping), handle generic access
        etype = data.get("type")

        if etype == "PROPOSAL_SUBMITTED":
            self._proposals.add(data["proposal_id"])
            self._votes[data["proposal_id"]] = {}
        
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

    def _admit(
        self,
        *,
        correlation_id: str,
        deterministic: Mapping[str, object],
        observational: Mapping[str, object] | None = None,
    ) -> AdmissionRecord:
        return shape_input(
            correlation_id=correlation_id,
            deterministic=deterministic,
            observational=observational,
        )

    def submit_proposal(self, raw: Mapping[str, object]) -> str:
        pid = str(uuid.uuid4())
        base_id = str(uuid.uuid4()) # Correlation for this flow
        admission = self._admit(
            correlation_id=base_id,
            deterministic={"text": raw["text"]},
            observational=raw.get("observational") if isinstance(raw.get("observational"), Mapping) else None,
        )
        event = VotingEvents.proposal_submitted(admission, pid)
        self._append(event)
        return pid

    def check_eligibility(self, raw: Mapping[str, object]) -> bool:
        admission = self._admit(
            correlation_id=str(uuid.uuid4()),
            deterministic={
                "user_id": raw["user_id"],
                "eligible": raw["eligible"],
            },
            observational=raw.get("proof") if isinstance(raw.get("proof"), Mapping) else None,
        )
        eligible = admission.deterministic["eligible"]
        if not isinstance(eligible, bool):
            raise ValueError("eligible must be a boolean")
        
        # 1. Emit Observational Proof (Records that we checked, and what we saw)
        proof_event = VotingEvents.eligibility_checked(admission)
        self._append(proof_event)
        
        if eligible:
            # 2. Emit Normative Decision (If check passed)
            decision_event = VotingEvents.voter_admitted(admission)
            self._append(decision_event)
            return True
        else:
            return False

    def cast_vote(self, raw: Mapping[str, object]) -> bool:
        # 1. Check constraints (Boundary logic)
        if raw["proposal_id"] not in self._proposals:
            raise ValueError("Unknown proposal")
        if raw["user_id"] not in self._eligible_users:
            raise ValueError("User not eligible (must pass check_eligibility first)")
        if raw["proposal_id"] in self._certified_results:
            raise ValueError("Voting closed")

        admission = self._admit(
            correlation_id=str(uuid.uuid4()),
            deterministic={
                "proposal_id": raw["proposal_id"],
                "user_id": raw["user_id"],
                "vote": raw["vote"],
            },
            observational=raw.get("observational") if isinstance(raw.get("observational"), Mapping) else None,
        )
        event = VotingEvents.vote_cast(admission)
        self._append(event)
        return True

    def certify_result(self, raw: Mapping[str, object]) -> dict:
        if raw["proposal_id"] not in self._proposals:
            raise ValueError("Unknown proposal")
        
        # Calculate tally from projection
        votes = self._votes.get(raw["proposal_id"], {})
        tally = {"Yes": 0, "No": 0}
        for v in votes.values():
            if v in tally:
                tally[v] += 1
            else:
                tally[v] = tally.get(v, 0) + 1
        
        admission = self._admit(
            correlation_id=str(uuid.uuid4()),
            deterministic={"proposal_id": raw["proposal_id"]},
            observational=raw.get("observational") if isinstance(raw.get("observational"), Mapping) else None,
        )
        event = VotingEvents.result_certified(admission, tally)
        self._append(event)
        return tally

    def get_log_digest(self) -> str:
        return self.v.digest()
