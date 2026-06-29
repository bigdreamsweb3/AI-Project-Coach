from datetime import datetime
from pathlib import Path

from ..coaching.rule_proposals import RuleProposal


def append_rule_proposal(
    path: Path,
    mode: str,
    question: str,
    proposal: RuleProposal,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"\n## {timestamp} - {mode}\n\n"
        f"Question\n{question.strip()}\n\n"
        f"Proposed Rule\n{proposal.rule_text}\n\n"
        f"Reason\n{proposal.reason}\n"
    )

    with path.open("a", encoding="utf-8") as file:
        file.write(entry)


def approve_rule(rules_path: Path, proposal: RuleProposal) -> bool:
    existing = rules_path.read_text(encoding="utf-8") if rules_path.exists() else ""
    if proposal.rule_text in existing:
        return False

    with rules_path.open("a", encoding="utf-8") as file:
        file.write(f"\n## Approved Coach Rule - {proposal.title}\n\n{proposal.rule_text}\n")
    return True
