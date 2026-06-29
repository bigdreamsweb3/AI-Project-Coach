from .ai.clients import AiConfigurationError, AiRouter, build_ai_router
from .ai.prompts import live_answer_prompt, model_answer_prompt, practice_question_prompt
from .core.config import build_config
from .core.types import AudienceType, ConceptsFile, PracticeQuestion, ProjectUnderstanding
from .knowledge.analogies import get_analogies_for_concepts, should_use_analogy
from .knowledge.concepts_editor import (
    get_custom_analogies,
    load_concepts_file,
    merge_concepts_with_edits,
    save_concepts_file,
)
from .knowledge.loader import load_project_understanding, load_project_knowledge
from .speech.recognizer import SpeechRecognizer
from .ui.live import run_live_interview_ui
from .ui.practice import run_practice_ui


class TrustLinkCoach:
    def __init__(self) -> None:
        self.config = build_config()
        self.knowledge = load_project_knowledge(self.config.source_paths)
        self.understanding = load_project_understanding(self.config.source_paths)
        self.concepts_file = load_concepts_file(self.config.concepts_path)
        self.ai: AiRouter = build_ai_router(self.config)
        self.speech = SpeechRecognizer()

    def get_ai_response(self, prompt: str, max_tokens: int = 150) -> str:
        response = self.ai.generate(prompt, max_tokens)
        print(f"AI used: {self.ai.last_model_label()}")
        return response

    def set_audience(self, audience: AudienceType) -> None:
        """Change audience type mid-session. Future generations will use the new audience."""
        object.__setattr__(self.config, 'audience_type', audience)
        print(f"Audience changed to: {audience.value}")

    def get_audience(self) -> AudienceType:
        """Get current audience type."""
        return self.config.audience_type

    def get_detected_concepts(self) -> list[str]:
        """Get list of auto-detected concept names."""
        return [concept.name for concept in self.understanding.system_concepts]

    def get_merged_concepts(self) -> list[str]:
        """Get list of concept names after applying user edits."""
        merged = merge_concepts_with_edits(
            self.understanding.system_concepts,
            self.concepts_file,
        )
        return [c.name for c in merged]

    def _get_system_concepts(self) -> list[str]:
        """Get system concept names for prompt injection (with edits applied)."""
        return self.get_merged_concepts()

    def _get_analogies(self, max_count: int = 3) -> list[str]:
        """Get relevant analogies for current audience (including custom)."""
        if not should_use_analogy(self.config.audience_type.value):
            return []

        # Get built-in analogies
        concepts = self.get_detected_concepts()
        analogies = get_analogies_for_concepts(concepts, self.config.audience_type.value, max_count)

        # Add custom analogies
        custom_analogies = get_custom_analogies(
            self.concepts_file,
            self.understanding.system_concepts,
            self.config.audience_type.value,
        )
        analogies.extend(custom_analogies)

        return analogies[:max_count]

    def get_concepts_file(self) -> ConceptsFile:
        """Get the current concepts file."""
        return self.concepts_file

    def save_concepts(self) -> None:
        """Save current concepts file to disk."""
        save_concepts_file(self.config.concepts_path, self.concepts_file)
        print(f"Concepts saved to: {self.config.concepts_path}")

    def reload_concepts(self) -> None:
        """Reload concepts from disk."""
        self.concepts_file = load_concepts_file(self.config.concepts_path)

    def create_practice_question(self) -> PracticeQuestion:
        question = self.get_ai_response(
            practice_question_prompt(
                self.knowledge,
                self.config.project_name,
                self.config.practice_context_chars,
                self.config.project_rules,
                audience_type=self.config.audience_type.value,
                system_concepts=self._get_system_concepts(),
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
                    audience_type=self.config.audience_type.value,
                    system_concepts=self._get_system_concepts(),
                    analogies=self._get_analogies(),
                ),
                self.config.answer_max_tokens,
            )
        return PracticeQuestion(question=question, model_answer=model_answer)

    def generate_live_cues(
        self,
        transcript: str,
        context_chars: int,
        project_rules: str,
        is_final: bool = True,
    ) -> str:
        """Generate live interview answer cues."""
        return self.get_ai_response(
            live_answer_prompt(
                self.knowledge,
                transcript,
                self.config.project_name,
                self.config.speaker_name,
                context_chars,
                project_rules,
                is_final=is_final,
                audience_type=self.config.audience_type.value,
                system_concepts=self._get_system_concepts(),
                analogies=self._get_analogies(max_count=2),
            ),
            self.config.live_draft_max_tokens,
        )

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
    print(f"Audience: {coach.config.audience_type.value}")
    print(f"Provider order: {', '.join(coach.config.provider_order)}")
    print(f"Configured AI models: {coach.ai.active_models_label()}")
    print(f"Practice model answers: {'on' if coach.config.practice_model_answer_enabled else 'off'}")
    print(f"Detected system concepts: {len(coach.get_detected_concepts())}")
    print(f"Custom concepts: {len(coach.concepts_file.custom_concepts)}")
    print("Knowledge sources:")
    for source_path in coach.config.source_paths:
        print(f"  - {source_path}")
    print(f"Rules: {coach.config.rules_path}")
    print(f"Concepts: {coach.config.concepts_path}")
    print(f"Proposal review max tokens: {coach.config.proposal_max_tokens}")
    print("1. Practice Mode (with UI)")
    print("2. Live Interview Mode")

    choice = input("Choose (1 or 2): ")
    if choice == "1":
        coach.practice_mode()
    else:
        coach.live_mode()
