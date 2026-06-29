def practice_question_prompt(knowledge: str, project_name: str, context_chars: int) -> str:
    return f"""You are an experienced technical project-defense interviewer.
Project name: {project_name}
Project context: {knowledge[:context_chars]}

Ask one strong technical question about the project architecture, product design, security model, implementation decisions, or user value.
Keep the question short and direct."""


def model_answer_prompt(question: str, project_name: str, speaker_name: str, context_chars: int) -> str:
    return f"""Give a strong project-defense answer for {project_name}.
Answer as {speaker_name}. Use technical confidence, clear reasoning, and plain language the builder can practice.
Return short speaking cues, not a script. Use 4 to 6 bullets. Each bullet should sound natural when spoken.

Question: {question}"""


def live_answer_prompt(
    knowledge: str,
    question: str,
    project_name: str,
    speaker_name: str,
    context_chars: int,
    is_final: bool = True,
) -> str:
    status = (
        "The interviewer has likely finished the question."
        if is_final
        else "The interviewer may still be talking, so infer carefully and refine the answer around the transcript so far."
    )

    return f"""Project name: {project_name}
Project context: {knowledge[:context_chars]}

Interview transcript: {question}

Status: {status}

Give {speaker_name} short speaking cues, not a script. Use 4 to 6 bullets.
Each bullet should be a natural point to say next in a real conversation."""
