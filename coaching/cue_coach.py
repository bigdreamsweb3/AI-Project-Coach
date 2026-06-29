import re


STOP_WORDS = {
    "about",
    "after",
    "also",
    "because",
    "before",
    "being",
    "between",
    "could",
    "from",
    "have",
    "into",
    "that",
    "their",
    "there",
    "this",
    "through",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
    "your",
}


def extract_cues(answer: str) -> list[str]:
    cues: list[str] = []
    for raw_line in answer.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        cleaned = re.sub(r"^(?:[-*]|\d+[.)])\s+", "", line).strip()
        cleaned = cleaned.strip("*").strip()
        if cleaned and not cleaned.lower().startswith(("here", "answer", "suggested")):
            cues.append(cleaned)

    if len(cues) <= 1:
        sentences = re.split(r"(?<=[.!?])\s+", answer.strip())
        cues = [sentence.strip() for sentence in sentences if sentence.strip()]

    return cues[:6]


def cue_matches_spoken_text(cue: str, spoken_text: str) -> bool:
    cue_terms = _important_terms(cue)
    spoken_terms = set(_important_terms(spoken_text))

    if not cue_terms or not spoken_terms:
        return False

    matches = sum(1 for term in cue_terms if term in spoken_terms)
    required = 1 if len(cue_terms) <= 3 else 2
    return matches >= required


def _important_terms(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    return [word for word in words if len(word) >= 4 and word not in STOP_WORDS]
