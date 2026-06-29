"""Analogy Library: Simple real-world explanations for technical concepts.

This module provides a library of analogies that help explain technical
concepts in everyday language. Analogies are selected based on:
- The system concept being explained
- The target audience
- Whether an analogy would genuinely help understanding

Usage:
    analogy = get_analogy_for_concept("Authentication Flow", "non-technical")
    # Returns: "Checking someone's ID before letting them into a building"
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Analogy:
    """A real-world analogy for a technical concept."""
    concept: str  # System concept name
    analogy: str  # The analogy text
    audience: str  # Best audience: non-technical, semi-technical, technical, expert
    conditions: list[str]  # When to use this analogy


# Core analogy library
ANALOGIES: list[Analogy] = [
    # Authentication analogies
    Analogy(
        concept="Authentication Flow",
        analogy="Checking someone's ID before letting them into a building",
        audience="non-technical",
        conditions=["login", "auth", "identity", "verify", "credential"],
    ),
    Analogy(
        concept="Authentication Flow",
        analogy="A hotel key card that only works for your room",
        audience="semi-technical",
        conditions=["session", "token", "jwt"],
    ),
    Analogy(
        concept="Session Validation",
        analogy="Showing your pass again before entering a restricted area",
        audience="non-technical",
        conditions=["session", "validate", "check", "re-authenticate"],
    ),

    # Payment/settlement analogies
    Analogy(
        concept="Payment Authorization Flow",
        analogy="A bank holding a check until both sides confirm the transaction",
        audience="non-technical",
        conditions=["payment", "transfer", "escrow", "settlement"],
    ),
    Analogy(
        concept="Payment Authorization Flow",
        analogy="An escrow service holding money until all conditions are met",
        audience="semi-technical",
        conditions=["vault", "hold", "escrow", "authorize"],
    ),
    Analogy(
        concept="Settlement",
        analogy="Finalizing a handshake after both parties agree on the terms",
        audience="non-technical",
        conditions=["settlement", "finalize", "complete"],
    ),

    # Privacy/encryption analogies
    Analogy(
        concept="Privacy Protection Flow",
        analogy="Locking information in a box only the right person can open",
        audience="non-technical",
        conditions=["encrypt", "decrypt", "cipher", "secret"],
    ),
    Analogy(
        concept="Privacy Protection Flow",
        analogy="Writing a letter in a code only you and the recipient understand",
        audience="semi-technical",
        conditions=["encode", "decode", "cryptography"],
    ),
    Analogy(
        concept="Privacy Protection Flow",
        analogy="Shredding personal documents before throwing them away",
        audience="non-technical",
        conditions=["mask", "redact", "sanitize", "pii", "gdpr"],
    ),

    # Notification analogies
    Analogy(
        concept="Notification Delivery Flow",
        analogy="A town crier announcing important news to everyone",
        audience="non-technical",
        conditions=["broadcast", "notify", "alert"],
    ),
    Analogy(
        concept="Notification Delivery Flow",
        analogy="A postal service that reliably delivers your letters",
        audience="semi-technical",
        conditions=["email", "sms", "webhook", "message"],
    ),

    # Validation analogies
    Analogy(
        concept="Input Validation Flow",
        analogy="A bouncer at a club checking if people meet the dress code",
        audience="non-technical",
        conditions=["validate", "check", "sanitize", "filter"],
    ),
    Analogy(
        concept="Input Validation Flow",
        analogy="A recipe that only accepts ingredients that match the dish",
        audience="semi-technical",
        conditions=["schema", "type", "format"],
    ),

    # Error handling analogies
    Analogy(
        concept="Error Handling Flow",
        analogy="A backup plan when the original plan falls apart",
        audience="non-technical",
        conditions=["error", "exception", "fallback", "retry"],
    ),
    Analogy(
        concept="Error Handling Flow",
        analogy="A circuit breaker that stops a fire from spreading",
        audience="semi-technical",
        conditions=["circuit", "breaker", "timeout"],
    ),

    # Audit/Logging analogies
    Analogy(
        concept="Audit Trail Flow",
        analogy="A receipt book that records every important transaction",
        audience="non-technical",
        conditions=["audit", "log", "history", "track"],
    ),
    Analogy(
        concept="Audit Trail Flow",
        analogy="Security cameras that record everything for later review",
        audience="semi-technical",
        conditions=["event", "activity", "history"],
    ),

    # Rate limiting analogies
    Analogy(
        concept="Rate Limiting Flow",
        analogy="A venue with limited seating that stops letting people in when full",
        audience="non-technical",
        conditions=["rate", "limit", "quota", "throttle"],
    ),
    Analogy(
        concept="Rate Limiting Flow",
        analogy="A bouncer counting how many people enter and enforcing a cap",
        audience="semi-technical",
        conditions=["rate", "limit", "cap"],
    ),

    # Cache analogies
    Analogy(
        concept="Cache Management Flow",
        analogy="A frequently-used shelf near the front of a library",
        audience="non-technical",
        conditions=["cache", "fast", "performance", "hit"],
    ),
    Analogy(
        concept="Cache Management Flow",
        analogy="Keeping commonly-needed items on your desk instead of in a distant file cabinet",
        audience="semi-technical",
        conditions=["cache", "store", "memory", "retrieve"],
    ),
]


def get_analogy_for_concept(concept: str, audience: str) -> Optional[str]:
    """Get the best analogy for a concept and audience.

    Args:
        concept: The system concept name (e.g., "Authentication Flow")
        audience: Target audience type (non-technical, semi-technical, technical, expert)

    Returns:
        An appropriate analogy string, or None if no good match exists
    """
    concept_lower = concept.lower()
    best_match: Optional[Analogy] = None

    for analogy in ANALOGIES:
        # Check if concept matches
        if concept_lower in analogy.concept.lower() or analogy.concept.lower() in concept_lower:
            # Check if audience matches
            audience_score = _get_audience_score(audience, analogy.audience)

            if best_match is None or audience_score > _get_audience_score(audience, best_match.audience):
                best_match = analogy

    # If no concept-specific match, try keyword matching
    if best_match is None:
        for analogy in ANALOGIES:
            if any(condition in concept_lower for condition in analogy.conditions):
                if _get_audience_score(audience, analogy.audience) >= 1:
                    return analogy.analogy

        # For expert/technical audiences, don't force analogies
        if audience in ("technical", "expert"):
            return None

    return best_match.analogy if best_match else None


def get_analogies_for_concepts(concepts: list[str], audience: str, max_count: int = 3) -> list[str]:
    """Get analogies for multiple concepts, limited in count.

    Args:
        concepts: List of system concept names
        audience: Target audience
        max_count: Maximum number of analogies to return

    Returns:
        List of analogy strings
    """
    analogies: list[str] = []
    used_analogies: set[str] = set()

    for concept in concepts:
        if len(analogies) >= max_count:
            break

        analogy = get_analogy_for_concept(concept, audience)
        if analogy and analogy not in used_analogies:
            analogies.append(analogy)
            used_analogies.add(analogy)

    return analogies


def _get_audience_score(audience: str, analogy_audience: str) -> int:
    """Calculate how well an analogy matches an audience.

    Returns:
        2 = perfect match, 1 = adjacent match, 0 = poor match
    """
    audience = audience.lower()
    analogy_audience = analogy_audience.lower()

    if audience == analogy_audience:
        return 2

    # Non-technical can use semi-technical analogies
    if audience == "non-technical" and analogy_audience == "semi-technical":
        return 1

    # Semi-technical can use non-technical analogies
    if audience == "semi-technical" and analogy_audience == "non-technical":
        return 1

    # Technical can use semi-technical analogies
    if audience == "technical" and analogy_audience == "semi-technical":
        return 1

    return 0


def should_use_analogy(audience: str) -> bool:
    """Determine if analogies should be used for this audience.

    Args:
        audience: Target audience type

    Returns:
        True if analogies would help this audience
    """
    # Expert audience prefers direct explanations
    if audience == "expert":
        return False

    # Technical audience may find analogies unnecessary
    if audience == "technical":
        return False  # They're comfortable with technical terms

    # Default to using analogies for non-technical and semi-technical
    return True


def format_analogy_for_prompt(analogy: str, concept: str) -> str:
    """Format an analogy for inclusion in a prompt.

    Args:
        analogy: The analogy text
        concept: The concept being explained

    Returns:
        Formatted text suitable for a prompt
    """
    return f"Analogy for {concept}: {analogy}"
