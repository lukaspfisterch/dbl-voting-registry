from typing import Any, Mapping, Optional
from dbl_core.events.model import DblEvent, DblEventKind

class VotingEvents:
    @staticmethod
    def proposal_submitted(correlation_id: str, proposal_id: str, text: str) -> DblEvent:
        """
        Creates a PROPOSAL_SUBMITTED event (DECISION).
        Normative data: proposal_id, text.
        """
        return DblEvent(
            event_kind=DblEventKind.DECISION,
            correlation_id=correlation_id,
            data={
                "type": "PROPOSAL_SUBMITTED",
                "proposal_id": proposal_id,
                "text": text
            }
        )

    @staticmethod
    def eligibility_checked(correlation_id: str, user_id: str, proof_data: dict[str, Any]) -> DblEvent:
        """
        Creates an ELIGIBILITY_CHECKED event (PROOF).
        Strictly Observational. Does NOT affect normative state.
        This provides the audit trail for WHY a voter was admitted.
        """
        return DblEvent(
            event_kind=DblEventKind.PROOF,
            correlation_id=correlation_id,
            data={
                "type": "ELIGIBILITY_CHECKED",
                "user_id": user_id
            },
            observational={
                "proof_details": proof_data
            }
        )

    @staticmethod
    def voter_admitted(correlation_id: str, user_id: str) -> DblEvent:
        """
        Creates a VOTER_ADMITTED event (DECISION).
        Normative action: Authorizes the user to vote.
        Derived from a successful check, but stands alone as the authority.
        """
        return DblEvent(
            event_kind=DblEventKind.DECISION,
            correlation_id=correlation_id,
            data={
                "type": "VOTER_ADMITTED",
                "user_id": user_id
            }
        )

    @staticmethod
    def vote_cast(correlation_id: str, proposal_id: str, user_id: str, vote: str) -> DblEvent:
        """
        Creates a VOTE_CAST event (DECISION).
        Normative data: proposal_id, user_id, vote.
        """
        return DblEvent(
            event_kind=DblEventKind.DECISION,
            correlation_id=correlation_id,
            data={
                "type": "VOTE_CAST",
                "proposal_id": proposal_id,
                "user_id": user_id,
                "vote": vote
            }
        )

    @staticmethod
    def result_certified(correlation_id: str, proposal_id: str, tally: dict[str, int]) -> DblEvent:
        """
        Creates a RESULT_CERTIFIED event (DECISION).
        Normative data: proposal_id, tally.
        """
        return DblEvent(
            event_kind=DblEventKind.DECISION,
            correlation_id=correlation_id,
            data={
                "type": "RESULT_CERTIFIED",
                "proposal_id": proposal_id,
                "tally": tally
            }
        )
