from enum import Enum
from pathlib import Path
from dataclasses import dataclass


class AudienceType(str, Enum):
    NON_TECHNICAL = "non-technical"  # Investors, clients, laymen
    SEMI_TECHNICAL = "semi-technical"  # Founders, product people
    TECHNICAL = "technical"  # Engineers
    EXPERT = "expert"  # Auditors, security reviewers


@dataclass(frozen=True)
class CoachConfig:
    anthropic_api_key: str | None
    gemini_api_key: str | None
    anthropic_model: str
    gemini_model: str
    project_name: str
    speaker_name: str
    audience_type: AudienceType
    source_paths: tuple[Path, ...]
    rules_path: Path
    project_rules: str
    provider_order: tuple[str, ...]
    practice_model_answer_enabled: bool
    question_max_tokens: int
    answer_max_tokens: int
    live_draft_max_tokens: int
    proposal_max_tokens: int
    practice_context_chars: int
    live_context_chars: int
    live_regenerate_after_chars: int
    live_window_alpha: float
    min_answer_words: int
    min_answer_key_terms: int
    observations_path: Path
    improvement_proposals_path: Path
    concepts_path: Path


@dataclass(frozen=True)
class PracticeQuestion:
    question: str
    model_answer: str


@dataclass(frozen=True)
class SpeechChunk:
    text: str
    heard_audio: bool


@dataclass(frozen=True)
class SystemConcept:
    """A system-level concept extracted from implementation details."""
    name: str  # Human-readable system name
    purpose: str  # Why this system exists
    protection: str | None  # What it protects (if applicable)
    tradeoff: str | None  # Design tradeoff made (if applicable)
    raw_evidence: list[str]  # Implementation details that informed this concept


@dataclass(frozen=True)
class ProjectUnderstanding:
    """Complete understanding of a project at system level."""
    system_concepts: list[SystemConcept]
    purpose_extractions: list[str]  # "Why" statements from docs/comments
    analogies: list[str]  # Relevant analogies for current audience
    raw_knowledge: str  # Original knowledge for technical reference


class ExplanationQuality:
    """Lightweight tracking for explanation quality."""
    HELPFUL = "helpful"
    NEEDS_IMPROVEMENT = "needs_improvement"
    NOT_USEFUL = "not_useful"


@dataclass(frozen=True)
class CustomConcept:
    """User-defined or edited system concept."""
    original_name: str  # Original detected name (if edited) or new name
    name: str  # Current name (may be edited)
    purpose: str | None  # Optional purpose clarification
    protection: str | None  # Optional protection clarification
    is_active: bool  # Whether this concept should be used
    is_merged: bool  # Whether this concept was merged from others
    merged_from: list[str]  # Names of concepts merged into this one


@dataclass(frozen=True)
class CustomAnalogy:
    """User-defined analogy for a concept."""
    concept_pattern: str  # Pattern to match (concept name or keyword)
    analogy: str  # The analogy text
    audience: str  # Target audience: non-technical, semi-technical, or any


@dataclass
class ConceptsFile:
    """Persisted user edits to detected system concepts."""
    custom_concepts: list[CustomConcept]
    custom_analogies: list[CustomAnalogy]
    quality_notes: list[str]  # User notes about explanation quality
