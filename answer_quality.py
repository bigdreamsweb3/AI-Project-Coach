import re

from .cue_coach import STOP_WORDS


def is_meaningful_answer(text: str, min_words: int, min_key_terms: int) -> bool:
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    if len(words) < min_words:
        return False

    key_terms = {word for word in words if len(word) >= 4 and word not in STOP_WORDS}
    return len(key_terms) >= min_key_terms


def answer_guidance(text: str, min_words: int, min_key_terms: int) -> str:
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    key_terms = {word for word in words if len(word) >= 4 and word not in STOP_WORDS}

    if not words:
        return "No answer was captured yet."

    if len(words) < min_words:
        return f"Keep going. Captured {len(words)} words; need at least {min_words} meaningful words."

    if len(key_terms) < min_key_terms:
        return f"Add more project-specific detail. Captured {len(key_terms)} key terms; need at least {min_key_terms}."

    return "Answer has enough context to capture."
