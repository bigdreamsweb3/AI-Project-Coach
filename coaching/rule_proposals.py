import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ai.clients import AiRouter


@dataclass(frozen=True)
class RuleProposal:
    title: str
    reason: str
    rule_text: str


def propose_rules_from_observation(
    ai: "AiRouter",
    project_name: str,
    knowledge: str,
    question: str,
    guidance: str,
    project_rules: str,
    context_chars: int,
    max_tokens: int,
) -> list[RuleProposal]:
    prompt = _proposal_prompt(project_name, knowledge, question, guidance, project_rules, context_chars)
    raw_response = ai.generate(prompt, max_tokens=max_tokens)
    return _parse_proposals(raw_response, project_rules)


def _proposal_prompt(
    project_name: str,
    knowledge: str,
    question: str,
    guidance: str,
    project_rules: str,
    context_chars: int,
) -> str:
    return f"""You are a senior coach-quality reviewer for Project Coach.
Project: {project_name}

Design philosophy: Think in Code. Speak in Systems.
The coach should internally understand implementation details but externally communicate using system-level concepts, purposes, and protections.

Authoritative project rules:
{project_rules or "No active project rules have been approved yet."}

Project context:
{knowledge[:context_chars]}

Observation question:
{question}

Observation guidance:
{guidance}

Decide whether this observation reveals an issue where the coach could better explain the project's systems:

Evaluate for these proposal-worthy issues:
1. The coach surfaces implementation details (function names, API routes) instead of system purposes
2. The coach answers in technical jargon rather than concept-focused language
3. The coach missed a security, privacy, or architectural protection that should be highlighted
4. The coach failed to explain WHY a design choice exists, not just what it does
5. The coach's language would confuse a non-technical audience when a simpler explanation exists

Do NOT propose rules for:
- Technical inaccuracies (the project rules handle this)
- Questions outside the project's scope
- Implementation-specific details that don't represent system-level thinking

Rules:
- Prefer improving the coach's ability to explain systems over changing project facts
- Do not invent facts not supported by the project context or active rules
- Prefer one strong proposal over many weak proposals
- Return strict JSON only
- Use this exact shape:
{{"proposals":[{{"title":"short title","reason":"why this improves coaching quality","rule_text":"- Approved coach rule written as one clear bullet"}}]}}
- Return {{"proposals":[]}} when no proposal is needed."""


def _parse_proposals(raw_response: str, project_rules: str) -> list[RuleProposal]:
    data = _load_json_object(raw_response)
    raw_proposals = data.get("proposals", []) if isinstance(data, dict) else []
    if not isinstance(raw_proposals, list):
        return []

    proposals: list[RuleProposal] = []
    for item in raw_proposals[:3]:
        if not isinstance(item, dict):
            continue

        title = _clean_field(item.get("title"))
        reason = _clean_field(item.get("reason"))
        rule_text = _clean_field(item.get("rule_text"))
        if not title or not reason or not rule_text:
            continue

        if not rule_text.startswith("-"):
            rule_text = f"- {rule_text}"

        if rule_text in project_rules:
            continue

        proposals.append(RuleProposal(title=title, reason=reason, rule_text=rule_text))

    return proposals


def _load_json_object(raw_response: str) -> object:
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_response, flags=re.DOTALL)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}


def _clean_field(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())
