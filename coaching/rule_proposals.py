from dataclasses import dataclass


@dataclass(frozen=True)
class RuleProposal:
    title: str
    reason: str
    rule_text: str


AUTH_CONFLICT_TERMS = (
    "username/password",
    "username password",
    "traditional username",
    "password login",
    "sms-based",
    "sms otp",
    "generic sms",
    "multiple authentication strategies",
    "different authentication strategies",
)


def propose_rules_from_observation(question: str, guidance: str, project_rules: str) -> list[RuleProposal]:
    text = f"{question}\n{guidance}".lower()
    proposals: list[RuleProposal] = []

    if any(term in text for term in AUTH_CONFLICT_TERMS):
        proposed_rule = (
            "- When a TrustLink auth question mentions multiple auth routes, username/password, "
            "or SMS auth, correct the premise: current account authentication is WhatsApp/phone "
            "OTP followed by TrustLink session and PIN handling; Web3 wallet connect auth is future roadmap only."
        )
        if proposed_rule not in project_rules:
            proposals.append(
                RuleProposal(
                    title="TrustLink auth premise correction",
                    reason="Observation framed current auth as multiple strategies or unsupported password/SMS auth.",
                    rule_text=proposed_rule,
                )
            )

    return proposals
