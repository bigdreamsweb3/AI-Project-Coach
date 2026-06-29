from .ai_clients import AiConfigurationError, AiRouter, build_ai_router
from .config import build_config
from .knowledge import load_project_knowledge
from .live_ui import run_live_interview_ui
from .prompts import model_answer_prompt, practice_question_prompt
from .speech import SpeechRecognizer
from .types import PracticeQuestion
from .ui import run_practice_ui


class TrustLinkCoach:
    def __init__(self) -> None:
        self.config = build_config()
        self.knowledge = load_project_knowledge(self.config.source_paths)
        self.ai: AiRouter = build_ai_router(self.config)
        self.speech = SpeechRecognizer()

    def get_ai_response(self, prompt: str, max_tokens: int = 150) -> str:
        return self.ai.generate(prompt, max_tokens)

    def create_practice_question(self) -> PracticeQuestion:
        question = self.get_ai_response(
            practice_question_prompt(
                self.knowledge,
                self.config.project_name,
                self.config.practice_context_chars,
            ),
            self.config.question_max_tokens,
        )
        model_answer = ""
        if self.config.practice_model_answer_enabled:
            model_answer = self.get_ai_response(
                model_answer_prompt(
                    question,
                    self.config.project_name,
                    self.config.speaker_name,
                    self.config.practice_context_chars,
                ),
                self.config.answer_max_tokens,
            )
        return PracticeQuestion(question=question, model_answer=model_answer)

    def listen(self) -> str:
        return self.speech.listen()

    def practice_mode(self) -> None:
        run_practice_ui(self)

    def live_mode(self) -> None:
        run_live_interview_ui(self)


def main() -> None:
    try:
        coach = TrustLinkCoach()
    except AiConfigurationError as exc:
        print(str(exc))
        raise SystemExit(1) from exc

    print("Project Coach Ready")
    print(f"Project: {coach.config.project_name}")
    print(f"Speaker: {coach.config.speaker_name}")
    print(f"Provider order: {', '.join(coach.config.provider_order)}")
    print(f"Practice model answers: {'on' if coach.config.practice_model_answer_enabled else 'off'}")
    print("Knowledge sources:")
    for source_path in coach.config.source_paths:
        print(f"  - {source_path}")
    print(f"Claude model: {coach.config.anthropic_model}")
    print(f"Gemini model: {coach.config.gemini_model}")
    print("1. Practice Mode (with UI)")
    print("2. Live Interview Mode")

    choice = input("Choose (1 or 2): ")
    if choice == "1":
        coach.practice_mode()
    else:
        coach.live_mode()
