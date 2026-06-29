"""System Translator: Converts implementation details into system-level concepts.

This module implements the "Think in Code, Speak in Systems" principle by
translating raw implementation evidence into human-readable system concepts.
"""

import re
from dataclasses import dataclass

from ..core.types import SystemConcept


# Pattern definitions for detecting implementation patterns
IMPLEMENTATION_PATTERNS: list[tuple[str, str, str, list[str], str | None]] = [
    # (pattern_name, system_name, purpose_template, evidence_keywords, protection_template)
    (
        "auth_flow",
        "Authentication Flow",
        "Verifies user identity before granting access",
        ["login", "auth", "authenticate", "credential", "password", "token", "jwt", "session", "signin", "sign-in"],
        "Prevents unauthorized access to user accounts",
    ),
    (
        "payment_flow",
        "Payment Authorization Flow",
        "Validates and authorizes financial transactions",
        ["payment", "pay", "transaction", "transfer", "vault", "escrow", "settlement", "stripe", "checkout"],
        "Ensures money moves only when authorized",
    ),
    (
        "privacy_flow",
        "Privacy Protection Flow",
        "Protects sensitive data from unauthorized access",
        ["encrypt", "decrypt", "hash", "privacy", "mask", "redact", "sanitize", "pii", "gdpr"],
        "Keeps sensitive information private and compliant",
    ),
    (
        "notification_flow",
        "Notification Delivery Flow",
        "Informs users and systems about events",
        ["notification", "notify", "webhook", "email", "sms", "alert", "message", "push"],
        "Ensures important events reach the right people",
    ),
    (
        "data_flow",
        "Data Persistence Flow",
        "Stores and retrieves application data reliably",
        ["database", "save", "load", "query", "fetch", "store", "persist", "model", "schema", "migration"],
        "Preserves data integrity and availability",
    ),
    (
        "validation_flow",
        "Input Validation Flow",
        "Ensures data meets expected formats and constraints",
        ["validate", "validation", "sanitize", "schema", "type", "format", "check"],
        "Prevents invalid data from entering the system",
    ),
    (
        "error_flow",
        "Error Handling Flow",
        "Manages unexpected situations gracefully",
        ["error", "exception", "retry", "fallback", "timeout", "circuit"],
        "Maintains system stability under failure conditions",
    ),
    (
        "audit_flow",
        "Audit Trail Flow",
        "Records important actions for accountability",
        ["audit", "log", "history", "track", "event", "activity"],
        "Provides accountability and helps investigate issues",
    ),
    (
        "rate_limit_flow",
        "Rate Limiting Flow",
        "Controls how frequently operations can occur",
        ["rate", "limit", "quota", "throttle", "cap"],
        "Protects system resources and prevents abuse",
    ),
    (
        "cache_flow",
        "Cache Management Flow",
        "Speeds up repeated data access",
        ["cache", "cache", "memcached", "redis", "store", "hit", "miss"],
        "Improves performance through faster data retrieval",
    ),
]


@dataclass
class TranslationResult:
    """Result of translating implementation evidence into a system concept."""
    concept: SystemConcept
    confidence: float  # 0.0 to 1.0
    matched_pattern: str
    evidence_snippets: list[str]


def detect_system_concepts(knowledge: str) -> list[TranslationResult]:
    """Analyze raw knowledge and detect system-level concepts.

    Args:
        knowledge: Raw implementation knowledge (code snippets, file paths, etc.)

    Returns:
        List of detected system concepts with confidence scores
    """
    knowledge_lower = knowledge.lower()
    results: list[TranslationResult] = []
    seen_concepts: set[str] = set()

    for pattern_name, system_name, purpose, keywords, protection in IMPLEMENTATION_PATTERNS:
        # Count keyword matches
        match_count = 0
        evidence_snippets: list[str] = []

        for keyword in keywords:
            if keyword in knowledge_lower:
                match_count += 1
                # Extract surrounding context for evidence
                pattern = rf".{{0,60}}{re.escape(keyword)}.{{0,60}}"
                matches = re.findall(pattern, knowledge_lower, re.IGNORECASE)
                for match in matches[:2]:  # Keep up to 2 snippets per keyword
                    clean_snippet = match.strip()
                    if clean_snippet and len(clean_snippet) > 20:
                        evidence_snippets.append(clean_snippet)

        # Calculate confidence based on keyword coverage
        if match_count > 0:
            confidence = min(1.0, match_count / 3.0)  # 3+ keywords = full confidence

            # Avoid duplicate concepts
            if system_name not in seen_concepts:
                seen_concepts.add(system_name)
                concept = SystemConcept(
                    name=system_name,
                    purpose=purpose,
                    protection=protection,
                    tradeoff=None,
                    raw_evidence=evidence_snippets[:5],
                )
                results.append(TranslationResult(
                    concept=concept,
                    confidence=confidence,
                    matched_pattern=pattern_name,
                    evidence_snippets=evidence_snippets,
                ))

    # Sort by confidence
    results.sort(key=lambda r: r.confidence, reverse=True)
    return results


def format_system_summary(concepts: list[TranslationResult]) -> str:
    """Format detected system concepts into a readable summary.

    Args:
        concepts: Detected system concepts

    Returns:
        Formatted system summary string
    """
    if not concepts:
        return "No system patterns detected in the provided code."

    lines = ["## Detected System Concepts\n"]
    for result in concepts:
        concept = result.concept
        lines.append(f"\n### {concept.name} (confidence: {result.confidence:.0%})")
        lines.append(f"**Purpose**: {concept.purpose}")
        if concept.protection:
            lines.append(f"**Protection**: {concept.protection}")

        if concept.raw_evidence:
            lines.append("\n**Evidence found**:")
            for i, evidence in enumerate(concept.raw_evidence[:3], 1):
                # Clean up the snippet
                clean = evidence.replace("\n", " ").strip()
                if len(clean) > 80:
                    clean = clean[:77] + "..."
                lines.append(f"  {i}. {clean}")

    return "\n".join(lines)


def extract_function_purpose(function_code: str) -> str | None:
    """Try to extract the stated purpose from a function's code or docstring.

    Args:
        function_code: Source code of a function

    Returns:
        Extracted purpose or None if not found
    """
    # Try docstring first
    docstring_match = re.search(r'"""(.*?)"""', function_code, re.DOTALL)
    if docstring_match:
        docstring = docstring_match.group(1).strip()
        if docstring:
            # Take first sentence or line
            first_line = docstring.split(".")[0].strip()
            if len(first_line) > 10:
                return first_line

    # Try comment before function
    comment_match = re.search(r"#\s*(.+?)(?:\n|$)", function_code)
    if comment_match:
        comment = comment_match.group(1).strip()
        if len(comment) > 10 and not comment.startswith("TODO"):
            return comment

    return None


def translate_endpoint(endpoint_def: str) -> str:
    """Convert an API endpoint definition to system-level language.

    Args:
        endpoint_def: Raw endpoint definition (e.g., "POST /api/auth/login")

    Returns:
        System-level description
    """
    # Common endpoint patterns
    endpoint_map = {
        "auth": "Authentication",
        "login": "Authentication",
        "signup": "Registration",
        "register": "Registration",
        "user": "User Management",
        "profile": "Profile Management",
        "payment": "Payment Processing",
        "checkout": "Checkout Flow",
        "order": "Order Management",
        "product": "Product Catalog",
        "search": "Search",
        "notification": "Notifications",
        "webhook": "External Notifications",
        "admin": "Administration",
        "config": "Configuration",
        "health": "Health Check",
        "status": "Status Check",
    }

    endpoint_lower = endpoint_def.lower()

    for pattern, system in endpoint_map.items():
        if pattern in endpoint_lower:
            # Determine the action
            if any(method in endpoint_lower for method in ["post", "put", "patch"]):
                action = "modify"
            elif "delete" in endpoint_lower:
                action = "remove"
            else:
                action = "access"

            return f"{system} {action.title()}"

    return "Data Access"


def get_audience_adjustment(audience: str) -> dict[str, str]:
    """Get language adjustment hints for different audience types.

    Args:
        audience: Audience type (non-technical, semi-technical, technical, expert)

    Returns:
        Dictionary with language adjustment hints
    """
    adjustments = {
        "non-technical": {
            "detail_level": "high",
            "analogy_preference": "always",
            "technical_terms": "avoid",
            "abstraction": "maximum",
        },
        "semi-technical": {
            "detail_level": "medium",
            "analogy_preference": "helpful",
            "technical_terms": "minimal",
            "abstraction": "high",
        },
        "technical": {
            "detail_level": "medium-high",
            "analogy_preference": "optional",
            "technical_terms": "allowed",
            "abstraction": "balanced",
        },
        "expert": {
            "detail_level": "high",
            "analogy_preference": "rarely",
            "technical_terms": "expected",
            "abstraction": "minimum",
        },
    }

    return adjustments.get(audience.lower(), adjustments["non-technical"])
