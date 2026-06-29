from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class CoachConfig:
    anthropic_api_key: str | None
    gemini_api_key: str | None
    anthropic_model: str
    gemini_model: str
    project_name: str
    speaker_name: str
    source_paths: tuple[Path, ...]
    rules_path: Path
    project_rules: str
    provider_order: tuple[str, ...]
    practice_model_answer_enabled: bool
    question_max_tokens: int
    answer_max_tokens: int
    live_draft_max_tokens: int
    practice_context_chars: int
    live_context_chars: int
    live_regenerate_after_chars: int
    live_window_alpha: float
    min_answer_words: int
    min_answer_key_terms: int
    observation_log_path: Path
    rule_proposals_path: Path


@dataclass(frozen=True)
class PracticeQuestion:
    question: str
    model_answer: str


@dataclass(frozen=True)
class SpeechChunk:
    text: str
    heard_audio: bool
