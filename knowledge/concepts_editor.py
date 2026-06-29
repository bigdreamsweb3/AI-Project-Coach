"""Concepts Editor: Manage user edits to detected system concepts.

This module handles:
- Loading/saving custom concepts and analogies
- Merging user edits with auto-detected concepts
- Formatting concepts for prompt injection
"""

import re
from pathlib import Path

from ..core.types import ConceptsFile, CustomAnalogy, CustomConcept, SystemConcept


def load_concepts_file(path: Path) -> ConceptsFile:
    """Load user edits from the concepts file.

    Args:
        path: Path to the concepts file

    Returns:
        ConceptsFile with custom concepts and analogies
    """
    if not path.exists():
        return ConceptsFile(custom_concepts=[], custom_analogies=[], quality_notes=[])

    content = path.read_text(encoding="utf-8")
    custom_concepts: list[CustomConcept] = []
    custom_analogies: list[CustomAnalogy] = []
    quality_notes: list[str] = []

    current_section = None
    for line in content.splitlines():
        stripped = line.strip()

        # Track sections
        if stripped.startswith("## Custom Concepts"):
            current_section = "concepts"
            continue
        elif stripped.startswith("## Custom Analogies"):
            current_section = "analogies"
            continue
        elif stripped.startswith("## Quality Notes"):
            current_section = "notes"
            continue

        # Parse concepts
        if current_section == "concepts" and stripped.startswith("- "):
            concept = _parse_concept_line(stripped)
            if concept:
                custom_concepts.append(concept)

        # Parse analogies
        elif current_section == "analogies" and stripped.startswith("- "):
            analogy = _parse_analogy_line(stripped)
            if analogy:
                custom_analogies.append(analogy)

        # Parse quality notes
        elif current_section == "notes" and stripped.startswith("- "):
            note = stripped[2:].strip()
            if note:
                quality_notes.append(note)

    return ConceptsFile(
        custom_concepts=custom_concepts,
        custom_analogies=custom_analogies,
        quality_notes=quality_notes,
    )


def save_concepts_file(path: Path, concepts_file: ConceptsFile) -> None:
    """Save user edits to the concepts file.

    Args:
        path: Path to save to
        concepts_file: ConceptsFile with edits to save
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Project Coach - Custom Concepts & Analogies",
        "",
        "This file stores your customizations to auto-detected system concepts.",
        "Edits here persist across sessions.",
        "",
        "## Custom Concepts",
        "",
    ]

    # Write concepts
    for concept in concepts_file.custom_concepts:
        lines.append(_format_concept(concept))
        lines.append("")

    lines.extend(["", "## Custom Analogies", ""])

    # Write analogies
    for analogy in concepts_file.custom_analogies:
        lines.append(_format_analogy(analogy))
        lines.append("")

    lines.extend(["", "## Quality Notes", ""])

    # Write quality notes
    for note in concepts_file.quality_notes:
        lines.append(f"- {note}")

    path.write_text("\n".join(lines), encoding="utf-8")


def _parse_concept_line(line: str) -> CustomConcept | None:
    """Parse a concept line like: 'Authentication Flow [active] (purpose: x)'"""
    # Extract name
    name_match = re.match(r"-\s*(.+?)(?:\[|\()", line)
    if not name_match:
        # Simple case: just the name
        name = line[2:].strip().rstrip("*").strip()
        return CustomConcept(
            original_name=name,
            name=name,
            purpose=None,
            protection=None,
            is_active="[active]" in line or "*" not in line,
            is_merged=False,
            merged_from=[],
        )

    name = name_match.group(1).strip()
    is_active = "[active]" in line
    is_merged = "[merged]" in line

    # Extract purpose
    purpose_match = re.search(r"purpose:\s*(.+?)(?:\)|$)", line)
    purpose = purpose_match.group(1).strip() if purpose_match else None

    # Extract protection
    protection_match = re.search(r"protection:\s*(.+?)(?:\)|$)", line)
    protection = protection_match.group(1).strip() if protection_match else None

    # Extract merged from
    merged_from_match = re.search(r"merged from:\s*(.+?)(?:\)|$)", line)
    merged_from = []
    if merged_from_match:
        merged_from = [m.strip() for m in merged_from_match.group(1).split(",")]

    return CustomConcept(
        original_name=name,
        name=name,
        purpose=purpose,
        protection=protection,
        is_active=is_active,
        is_merged=is_merged,
        merged_from=merged_from,
    )


def _parse_analogy_line(line: str) -> CustomAnalogy | None:
    """Parse an analogy line like: '- Authentication: Like checking ID before entry [audience: non-technical]'"""
    # Extract pattern and analogy
    if ":" not in line:
        return None

    parts = line[2:].split(":", 1)
    if len(parts) != 2:
        return None

    pattern = parts[0].strip()
    rest = parts[1].strip()

    # Extract audience
    audience_match = re.search(r"\[audience:\s*(\w+[-\w]*)\]", rest)
    audience = audience_match.group(1) if audience_match else "any"

    # Extract analogy text (remove audience bracket)
    analogy = re.sub(r"\s*\[audience:.*\]", "", rest).strip()

    return CustomAnalogy(
        concept_pattern=pattern,
        analogy=analogy,
        audience=audience,
    )


def _format_concept(concept: CustomConcept) -> str:
    """Format a concept for saving."""
    parts = [f"- {concept.name}"]

    if concept.is_merged and concept.merged_from:
        parts.append(f"  merged from: {', '.join(concept.merged_from)}")

    extras = []
    if concept.purpose:
        extras.append(f"purpose: {concept.purpose}")
    if concept.protection:
        extras.append(f"protection: {concept.protection}")

    if extras:
        parts[0] += f" ({'; '.join(extras)})"

    parts[0] += " [active]" if concept.is_active else " [disabled]"

    return "\n".join(parts)


def _format_analogy(analogy: CustomAnalogy) -> str:
    """Format an analogy for saving."""
    audience_str = f" [audience: {analogy.audience}]" if analogy.audience != "any" else ""
    return f"- {analogy.concept_pattern}: {analogy.analogy}{audience_str}"


def merge_concepts_with_edits(
    detected: list[SystemConcept],
    edits: ConceptsFile,
) -> list[SystemConcept]:
    """Merge auto-detected concepts with user edits.

    Args:
        detected: Auto-detected system concepts
        edits: User edits from concepts file

    Returns:
        Merged list of concepts with edits applied
    """
    # Build a map of original names to edits
    edits_map: dict[str, CustomConcept] = {}
    for concept in edits.custom_concepts:
        edits_map[concept.original_name] = concept

    merged: list[SystemConcept] = []

    for concept in detected:
        edit = edits_map.get(concept.name)

        if edit and not edit.is_active:
            # Skip disabled concepts
            continue

        if edit:
            # Apply edits
            merged.append(SystemConcept(
                name=edit.name,
                purpose=edit.purpose or concept.purpose,
                protection=edit.protection or concept.protection,
                tradeoff=concept.tradeoff,
                raw_evidence=concept.raw_evidence,
            ))
        else:
            merged.append(concept)

    # Add any new concepts from edits (merges create new ones)
    for edit in edits.custom_concepts:
        if edit.is_merged:
            # Check if this merged concept is already added
            if not any(c.name == edit.name for c in merged):
                merged.append(SystemConcept(
                    name=edit.name,
                    purpose=edit.purpose or "User-defined system concept",
                    protection=edit.protection,
                    tradeoff=None,
                    raw_evidence=[],
                ))

    return merged


def get_custom_analogies(
    edits: ConceptsFile,
    detected_concepts: list[SystemConcept],
    audience: str,
) -> list[str]:
    """Get custom analogies for the current audience.

    Args:
        edits: User edits from concepts file
        detected_concepts: Detected concept names
        audience: Current audience type

    Returns:
        List of analogy strings suitable for prompts
    """
    analogies: list[str] = []
    concept_names = [c.name.lower() for c in detected_concepts]

    for analogy in edits.custom_analogies:
        # Check if this analogy matches any concept
        pattern_lower = analogy.concept_pattern.lower()
        if pattern_lower in concept_names or any(pattern_lower in name for name in concept_names):
            # Check audience match
            if analogy.audience in ("any", audience):
                analogies.append(analogy.analogy)

    return analogies


def format_concepts_for_prompt(concepts: list[SystemConcept], max_count: int = 5) -> str:
    """Format concepts for injection into prompts.

    Args:
        concepts: List of system concepts
        max_count: Maximum number to include

    Returns:
        Formatted string for prompt injection
    """
    if not concepts:
        return "No specific system concepts detected yet."

    lines = ["System concepts in this project:"]
    for concept in concepts[:max_count]:
        lines.append(f"- {concept.name}")
        if concept.purpose:
            lines.append(f"  Purpose: {concept.purpose}")
        if concept.protection:
            lines.append(f"  Protects: {concept.protection}")

    return "\n".join(lines)


def add_quality_note(concepts_file: ConceptsFile, note: str) -> ConceptsFile:
    """Add a quality note to the concepts file.

    Args:
        concepts_file: Current concepts file
        note: Note to add

    Returns:
        Updated ConceptsFile
    """
    return ConceptsFile(
        custom_concepts=concepts_file.custom_concepts,
        custom_analogies=concepts_file.custom_analogies,
        quality_notes=concepts_file.quality_notes + [note],
    )
