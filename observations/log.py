from datetime import datetime
from pathlib import Path


def append_observation(
    path: Path,
    mode: str,
    project_name: str,
    question: str,
    guidance: str,
    answer: str | None = None,
    explanation_quality: str | None = None,
) -> None:
    """Append an observation to the observations file.

    Args:
        path: Path to observations file
        mode: Mode (Practice Question, Live Interview Cues, etc.)
        project_name: Name of the project
        question: The question asked
        guidance: Guidance for the speaker
        answer: Optional captured answer
        explanation_quality: Optional quality rating (helpful, needs_improvement, not_useful)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    answer_section = f"\nAnswer Captured\n{answer.strip()}\n" if answer else ""
    quality_section = f"\nExplanation Quality\n{explanation_quality}\n" if explanation_quality else ""

    entry = (
        f"\n## {timestamp} - {mode}\n\n"
        f"Project\n{project_name}\n\n"
        f"Question\n{question.strip()}\n\n"
        f"Guidance\n{guidance.strip()}\n"
        f"{answer_section}"
        f"{quality_section}"
    )

    with path.open("a", encoding="utf-8") as file:
        file.write(entry)
