from datetime import datetime
from pathlib import Path


def append_observation(
    path: Path,
    mode: str,
    project_name: str,
    question: str,
    guidance: str,
    answer: str | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    answer_section = f"\nAnswer Captured\n{answer.strip()}\n" if answer else ""

    entry = (
        f"\n## {timestamp} - {mode}\n\n"
        f"Project\n{project_name}\n\n"
        f"Question\n{question.strip()}\n\n"
        f"Guidance\n{guidance.strip()}\n"
        f"{answer_section}"
    )

    with path.open("a", encoding="utf-8") as file:
        file.write(entry)
