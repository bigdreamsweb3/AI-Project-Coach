def practice_question_prompt(
    knowledge: str,
    project_name: str,
    context_chars: int,
    project_rules: str,
    audience_type: str = "non-technical",
    system_concepts: list[str] | None = None,
) -> str:
    concepts_section = ""
    if system_concepts:
        concepts_section = f"\nDetected system concepts in this project:\n" + "\n".join(f"- {c}" for c in system_concepts[:5])

    audience_guidance = _get_audience_question_guidance(audience_type)

    return f"""You are an experienced project-defense interviewer who helps developers understand their own architecture deeply.
Project name: {project_name}
Authoritative project rules:
{project_rules or "No separate project rules file was provided."}
{concepts_section}

Project context: {knowledge[:context_chars]}

Design philosophy: Think in Code. Speak in Systems.
- Internally understand implementation details (code patterns, API endpoints, function names, data structures)
- Externally communicate using system-level concepts (flows, protections, purposes, tradeoffs)
- When you detect a function like 'verify_identity()' or 'transfer_funds()', ask about the purpose and protection it provides

Target audience: {audience_type}
{audience_guidance}

Generate one strong question that helps the developer:
- Reflect on WHY they built something, not just what they built
- Explain the system-level purpose of an implementation choice
- Describe what their design protects, assumes, or enables
- Consider what an auditor, architect, or senior engineer would challenge

Good questions feel like they came from:
- a senior engineer reviewing the design
- an architect questioning the approach
- an auditor challenging assumptions
- a founder explaining the product to an investor

Example question styles:
- "Why is this step placed before that step? What would break if the order changed?"
- "What does this design protect against that a simpler approach cannot?"
- "What assumption does this architecture rely on? What would fail if that assumption were wrong?"
- "How would you explain this protection to someone who has never written code?"
- "What problem would appear if this check disappeared?"
- "What would an auditor challenge first about this flow?"

Keep the question short and direct. Ask one question that makes the developer think deeper about their own design.
Do not invent features, auth methods, security flows, or roadmap items that are not present in the authoritative rules or project context."""


def model_answer_prompt(
    question: str,
    project_name: str,
    speaker_name: str,
    context_chars: int,
    audience_type: str = "non-technical",
    system_concepts: list[str] | None = None,
    analogies: list[str] | None = None,
) -> str:
    concepts_section = ""
    if system_concepts:
        concepts_section = f"\nSystem concepts in this project:\n" + "\n".join(f"- {c}" for c in system_concepts[:5])

    analogies_section = ""
    if analogies:
        analogies_section = "\nAvailable analogies (use if helpful, don't force):\n" + "\n".join(f"- {a}" for a in analogies[:3])

    audience_guidance = _get_audience_answer_guidance(audience_type)

    return f"""You are helping {speaker_name} confidently explain {project_name} to an audience that is {audience_type.replace('-', ' ')}.

Design philosophy: Think in Code. Speak in Systems.
- Answer using concepts and purposes, not implementation details
- Explain the WHY behind each design choice
- Use simple real-world analogies when they genuinely help understanding
- Make a {audience_type.replace('-', ' ')} listener understand what the system is trying to accomplish

{audience_guidance}
{concepts_section}
{analogies_section}

Question: {question}

Give {speaker_name} 4 to 6 short speaking cues that sound like natural conversation, not reading from documentation.

Each cue should:
- Explain what the system DOES and WHY it exists
- Describe the protection or value it provides
- Use language appropriate for a {audience_type.replace('-', ' ')} listener
- Feel like confident explanation, not documentation recitation

Avoid:
- Leading with function names, API routes, or data structures
- Technical jargon that obscures purpose
- Reading like a textbook or API documentation

Think of this as training someone to give a confident TED-style explanation of their technical work."""


def live_answer_prompt(
    knowledge: str,
    question: str,
    project_name: str,
    speaker_name: str,
    context_chars: int,
    project_rules: str,
    is_final: bool = True,
    audience_type: str = "non-technical",
    system_concepts: list[str] | None = None,
    analogies: list[str] | None = None,
) -> str:
    status = (
        "The interviewer has likely finished the question."
        if is_final
        else "The interviewer may still be talking, so infer carefully and refine the answer around the transcript so far."
    )

    concepts_section = ""
    if system_concepts:
        concepts_section = f"\nSystem concepts:\n" + "\n".join(f"- {c}" for c in system_concepts[:5])

    analogies_section = ""
    if analogies:
        analogies_section = "\nAvailable analogies (use naturally):\n" + "\n".join(f"- {a}" for a in analogies[:2])

    audience_guidance = _get_audience_answer_guidance(audience_type)

    return f"""Project name: {project_name}
Authoritative project rules:
{project_rules or "No separate project rules file was provided."}
{concepts_section}

Project context: {knowledge[:context_chars]}

Interview transcript: {question}

Status: {status}

Target audience: {audience_type}
{audience_guidance}
{analogies_section}

Design philosophy: Think in Code. Speak in Systems.
- Internally understand implementation (code patterns, endpoints, functions)
- Externally communicate using concepts (purposes, protections, flows, tradeoffs)

Give {speaker_name} 4 to 6 short speaking cues for natural conversation, appropriate for a {audience_type.replace('-', ' ')} listener.

Each cue should:
- Explain what the system DOES and WHY it exists
- Describe the protection or value it provides
- Use language appropriate for the target audience
- Feel like confident explanation, not documentation recitation

Example cue styles:
- "Before anyone can proceed, the system double-checks that the identity presented is still trusted—similar to showing your boarding pass again before entering the aircraft."
- "Settlement happens only after both sides confirm—much like a bank holding funds until the transaction is verified."
- "This protection exists because without it, anyone could impersonate a legitimate user."

Avoid:
- Leading with function names, API routes, or technical jargon
- Reading like API documentation or code comments
- Mentioning features or flows not present in the project context

Do not invent features, auth methods, security flows, or roadmap items that are not supported by the authoritative rules or project context."""


def _get_audience_question_guidance(audience: str) -> str:
    """Get guidance for question generation based on audience type."""
    guidance = {
        "non-technical": (
            "Questions should be answerable without technical jargon. "
            "Focus on purpose, protection, and value rather than implementation."
        ),
        "semi-technical": (
            "Questions can reference some technical concepts but should emphasize "
            "business value, user benefit, and design rationale."
        ),
        "technical": (
            "Questions can include technical context. Focus on architectural decisions, "
            "tradeoffs, and engineering rationale."
        ),
        "expert": (
            "Questions can be highly technical. Focus on security implications, "
            "edge cases, scalability concerns, and deep architectural analysis."
        ),
    }
    return guidance.get(audience, guidance["non-technical"])


def _get_audience_answer_guidance(audience: str) -> str:
    """Get guidance for answer generation based on audience type."""
    guidance = {
        "non-technical": (
            "Use simple everyday language. Explain technical concepts using real-world comparisons. "
            "Focus on what the system does for people, not how it works technically."
        ),
        "semi-technical": (
            "Use some technical terms but always explain their meaning. "
            "Balance business value with technical context."
        ),
        "technical": (
            "You may use technical terms appropriately. Focus on how and why, not just what. "
            "Include relevant architectural and implementation context."
        ),
        "expert": (
            "Technical precision is expected. Focus on security, performance, scalability, "
            "and architectural tradeoffs. Assume deep technical understanding."
        ),
    }
    return guidance.get(audience, guidance["non-technical"])
