from typing import Any

from dbl_core.events.model import DblEvent, DblEventKind
from dbl_ingress.admission.model import AdmissionRecord

class VotingEvents:
    @staticmethod
    def proposal_submitted(admission: AdmissionRecord, proposal_id: str) -> DblEvent:
        """
        Creates a PROPOSAL_SUBMITTED event (DECISION).
        Normative data: proposal_id, text.
        """
        payload = {
            "type": "PROPOSAL_SUBMITTED",
            "proposal_id": proposal_id,
            **dict(admission.deterministic),
        }
        return DblEvent(
            event_kind=DblEventKind.DECISION,
            correlation_id=admission.correlation_id,
            data=payload,
        )

    @staticmethod
    def eligibility_checked(admission: AdmissionRecord) -> DblEvent:
        """
        Creates an ELIGIBILITY_CHECKED event (PROOF).
        Strictly Observational. Does NOT affect normative state.
        This provides the audit trail for WHY a voter was admitted.
        """
        proof_data: dict[str, Any] = dict(admission.observational or {})
        return DblEvent(
            event_kind=DblEventKind.PROOF,
            correlation_id=admission.correlation_id,
            data={
                "type": "ELIGIBILITY_CHECKED",
                "user_id": admission.deterministic["user_id"],
            },
            observational={
                "proof_details": proof_data,
            },
        )

    @staticmethod
    def voter_admitted(admission: AdmissionRecord) -> DblEvent:
        """
        Creates a VOTER_ADMITTED event (DECISION).
        Normative action: Authorizes the user to vote.
        Derived from a successful check, but stands alone as the authority.
        """
        return DblEvent(
            event_kind=DblEventKind.DECISION,
            correlation_id=admission.correlation_id,
            data={
                "type": "VOTER_ADMITTED",
                "user_id": admission.deterministic["user_id"],
            }
        )

    @staticmethod
    def vote_cast(admission: AdmissionRecord) -> DblEvent:
        """
        Creates a VOTE_CAST event (DECISION).
        Normative data: proposal_id, user_id, vote.
        """
        return DblEvent(
            event_kind=DblEventKind.DECISION,
            correlation_id=admission.correlation_id,
            data={
                "type": "VOTE_CAST",
                "proposal_id": admission.deterministic["proposal_id"],
                "user_id": admission.deterministic["user_id"],
                "vote": admission.deterministic["vote"],
            }
        )

    @staticmethod
    def result_certified(admission: AdmissionRecord, tally: dict[str, int]) -> DblEvent:
        """
        Creates a RESULT_CERTIFIED event (DECISION).
        Normative data: proposal_id, tally.
        """
        return DblEvent(
            event_kind=DblEventKind.DECISION,
            correlation_id=admission.correlation_id,
            data={
                "type": "RESULT_CERTIFIED",
                "proposal_id": admission.deterministic["proposal_id"],
                "tally": tally,
            }
        )
