import queue
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import TYPE_CHECKING

from ..coaching.answer_quality import answer_guidance, is_meaningful_answer
from ..coaching.rule_proposals import RuleProposal, propose_rules_from_observation
from ..core.constants import (
    LIVE_DONE_AFTER_SILENCE_SECONDS,
    LIVE_LISTEN_TIMEOUT_SECONDS,
    LIVE_PHRASE_TIME_LIMIT_SECONDS,
    WINDOW_GEOMETRY,
    WINDOW_TITLE,
)
from ..core.types import AudienceType, ExplanationQuality
from ..knowledge.concepts_editor import save_concepts_file
from ..observations.log import append_observation
from ..observations.rule_proposals import append_rule_proposal, approve_rule
from .listening_indicator import ListeningIndicator
from .text_format import append_markdown, append_plain, configure_rich_text

if TYPE_CHECKING:
    from ..app import TrustLinkCoach


def run_practice_ui(coach: "TrustLinkCoach") -> None:
    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry(WINDOW_GEOMETRY)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.9)

    events: queue.Queue[tuple[str, object]] = queue.Queue()
    listening_state = {"active": False, "last_audio_at": 0.0, "marked_done": False}
    answer_parts: list[str] = []
    current_question = {"text": ""}
    pending_rule_proposals: list[RuleProposal] = []
    last_cues_generated: list[str] = []

    indicator = ListeningIndicator(root)
    indicator.pack(fill=tk.X, padx=10, pady=(10, 0))

    model_label = tk.Label(
        root,
        text=f"AI models: {coach.ai.active_models_label()}",
        anchor="w",
        font=("Arial", 10),
    )
    model_label.pack(fill=tk.X, padx=10, pady=(4, 0))

    audience_label = tk.Label(
        root,
        text=f"Audience: {coach.config.audience_type.value}",
        anchor="w",
        font=("Arial", 10),
    )
    audience_label.pack(fill=tk.X, padx=10, pady=(2, 0))

    # Audience switcher
    audience_frame = tk.Frame(root)
    audience_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

    def on_audience_change(event):
        selected = audience_var.get()
        for aud in AudienceType:
            if aud.value == selected:
                coach.set_audience(aud)
                audience_label.configure(text=f"Audience: {aud.value}")
                break

    tk.Label(audience_frame, text="Switch audience:", font=("Arial", 9)).pack(side=tk.LEFT)
    audience_var = tk.StringVar(value=coach.config.audience_type.value)
    audience_combo = ttk.Combobox(
        audience_frame,
        textvariable=audience_var,
        values=[a.value for a in AudienceType],
        state="readonly",
        width=15,
        font=("Arial", 9),
    )
    audience_combo.pack(side=tk.LEFT, padx=5)
    audience_combo.bind("<<ComboboxSelected>>", on_audience_change)

    # Detected concepts display
    concepts_label = tk.Label(
        root,
        text=f"Detected concepts: {len(coach.get_detected_concepts())} | Merged: {len(coach.get_merged_concepts())}",
        anchor="w",
        font=("Arial", 9),
        fg="#666666",
    )
    concepts_label.pack(fill=tk.X, padx=10, pady=(0, 2))

    text_area = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        width=100,
        height=25,
        font=("Georgia", 11),
    )
    text_area.pack(padx=10, pady=10)
    configure_rich_text(text_area)

    def ask() -> None:
        listening_state["active"] = False
        answer_parts.clear()
        indicator.set_idle("Generating practice question")
        practice_question = coach.create_practice_question()
        current_question["text"] = practice_question.question
        last_cues_generated.clear()
        if practice_question.model_answer:
            last_cues_generated.extend([c.strip() for c in practice_question.model_answer.split('\n') if c.strip()])
        model_label.configure(text=f"AI models: {coach.ai.active_models_label()} | Last used: {coach.ai.last_model_label()}")

        append_plain(text_area, "\nQuestion\n", "label")
        append_markdown(text_area, practice_question.question)
        if practice_question.model_answer:
            append_plain(text_area, "\nModel Answer\n", "label")
            append_markdown(text_area, practice_question.model_answer)
        append_plain(text_area, "\nYour Answer\n", "label")
        append_observation(
            coach.config.observations_path,
            mode="Practice Question",
            project_name=coach.config.project_name,
            question=practice_question.question,
            guidance="Practice question generated in systems-thinking style. The speaker should answer using concepts and purposes—not implementation details.",
        )
        _show_rule_proposals(
            practice_question.question,
            "Practice question generated. Review any proposed rules before changing project truth.",
        )

        print("Speak your answer...")
        _start_answer_listener()

    def _start_answer_listener() -> None:
        listening_state["active"] = True
        listening_state["last_audio_at"] = time.monotonic()
        listening_state["marked_done"] = False
        indicator.set_listening("Listening for your answer")
        threading.Thread(target=_listen_for_answer, daemon=True).start()

    def _listen_for_answer() -> None:
        try:
            coach.speech.calibrate()
            events.put(("indicator", "listening"))

            while listening_state["active"]:
                chunk = coach.speech.listen_chunk(
                    timeout=LIVE_LISTEN_TIMEOUT_SECONDS,
                    phrase_time_limit=LIVE_PHRASE_TIME_LIMIT_SECONDS,
                )
                now = time.monotonic()

                if chunk.heard_audio:
                    listening_state["last_audio_at"] = now
                    listening_state["marked_done"] = False
                    events.put(("indicator", "talking"))
                    if chunk.text:
                        answer_parts.append(chunk.text)
                        events.put(("answer_text", chunk.text))
                    continue

                if now - listening_state["last_audio_at"] >= LIVE_DONE_AFTER_SILENCE_SECONDS:
                    answer_text = " ".join(answer_parts).strip()
                    if is_meaningful_answer(
                        answer_text,
                        coach.config.min_answer_words,
                        coach.config.min_answer_key_terms,
                    ):
                        listening_state["marked_done"] = True
                        listening_state["active"] = False
                        events.put(("done", answer_text))
                    else:
                        listening_state["last_audio_at"] = now
                        events.put(
                            (
                                "need_more",
                                answer_guidance(
                                    answer_text,
                                    coach.config.min_answer_words,
                                    coach.config.min_answer_key_terms,
                                ),
                            )
                        )
                    continue

                events.put(("indicator", "silence"))
        except Exception as exc:
            events.put(("error", str(exc)))

    def _process_events() -> None:
        while True:
            try:
                event, payload = events.get_nowait()
            except queue.Empty:
                break

            if event == "indicator":
                if payload == "talking":
                    indicator.set_talking("Speech detected")
                elif payload == "silence":
                    indicator.set_silence("Silence detected")
                else:
                    indicator.set_listening("Listening for your answer")
            elif event == "answer_text":
                append_plain(text_area, f"{payload} ")
            elif event == "done":
                indicator.set_done("Answer captured")
                append_plain(text_area, "\n\n")
                append_observation(
                    coach.config.observations_path,
                    mode="Practice Answer",
                    project_name=coach.config.project_name,
                    question=current_question["text"],
                    guidance="Answer captured after passing the local meaningful-context check. Speaker explained using system-level concepts.",
                    answer=str(payload),
                )
            elif event == "need_more":
                indicator.set_silence(str(payload))
            elif event == "error":
                indicator.set_error(str(payload))

        root.after(100, _process_events)

    def _show_rule_proposals(question: str, guidance: str) -> None:
        pending_rule_proposals.clear()
        try:
            pending_rule_proposals.extend(
                propose_rules_from_observation(
                    coach.ai,
                    coach.config.project_name,
                    coach.knowledge,
                    question,
                    guidance,
                    coach.config.project_rules,
                    coach.config.practice_context_chars,
                    coach.config.proposal_max_tokens,
                )
            )
            model_label.configure(text=f"AI models: {coach.ai.active_models_label()} | Last used: {coach.ai.last_model_label()}")
        except Exception as exc:
            indicator.set_error(f"Proposal review failed: {exc}")
            return

        if not pending_rule_proposals:
            return

        append_plain(text_area, "\nImprovement Proposal\n", "label")
        for proposal in pending_rule_proposals:
            append_plain(text_area, f"{proposal.title}\n{proposal.reason}\n{proposal.rule_text}\n")
            append_rule_proposal(
                coach.config.improvement_proposals_path,
                mode="Practice Question",
                question=question,
                proposal=proposal,
            )

    def _approve_pending_rule() -> None:
        if not pending_rule_proposals:
            indicator.set_idle("No pending rule proposal")
            return

        approved = 0
        for proposal in pending_rule_proposals:
            if approve_rule(coach.config.rules_path, proposal):
                approved += 1

        pending_rule_proposals.clear()
        indicator.set_done(f"Approved {approved} rule proposal(s)")
        append_plain(text_area, f"\nApproved {approved} rule proposal(s).\n")

    def _log_quality(quality: str) -> None:
        """Log explanation quality for the last generated cues."""
        if last_cues_generated:
            append_observation(
                coach.config.observations_path,
                mode="Explanation Quality",
                project_name=coach.config.project_name,
                question="N/A",
                guidance=f"Quality rating for last explanation: {quality}",
                answer="\n".join(last_cues_generated),
                explanation_quality=quality,
            )
            indicator.set_done(f"Logged quality: {quality}")
        else:
            indicator.set_idle("No explanation to rate yet")

    # Quality tracking buttons
    quality_frame = tk.Frame(root)
    quality_frame.pack(pady=5)
    tk.Label(quality_frame, text="Rate last explanation:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(quality_frame, text="Helpful", command=lambda: _log_quality(ExplanationQuality.HELPFUL), font=("Arial", 10), bg="#dcfce7").pack(side=tk.LEFT, padx=2)
    tk.Button(quality_frame, text="Needs Work", command=lambda: _log_quality(ExplanationQuality.NEEDS_IMPROVEMENT), font=("Arial", 10), bg="#fef08a").pack(side=tk.LEFT, padx=2)
    tk.Button(quality_frame, text="Not Useful", command=lambda: _log_quality(ExplanationQuality.NOT_USEFUL), font=("Arial", 10), bg="#fee2e2").pack(side=tk.LEFT, padx=2)

    # Concepts and analogies frame
    concepts_frame = tk.Frame(root)
    concepts_frame.pack(pady=5)

    def _open_concepts_editor():
        """Open a simple concepts editor dialog."""
        dialog = tk.Toplevel(root)
        dialog.title("Concept Editor")
        dialog.geometry("600x400")
        dialog.transient(root)
        dialog.grab_set()

        tk.Label(dialog, text="Edit Detected Concepts", font=("Arial", 12, "bold")).pack(pady=10)

        # Show detected concepts
        concepts_listbox = tk.Listbox(dialog, height=10, font=("Arial", 10))
        concepts_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        for concept_name in coach.get_detected_concepts():
            concepts_listbox.insert(tk.END, concept_name)

        # Custom analogy input
        analogy_frame = tk.Frame(dialog)
        analogy_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(analogy_frame, text="Add custom analogy:", font=("Arial", 10)).pack(anchor="w")
        concept_entry = tk.Entry(analogy_frame, width=30, font=("Arial", 10))
        concept_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(analogy_frame, text="like:").pack(side=tk.LEFT)
        analogy_entry = tk.Entry(analogy_frame, width=30, font=("Arial", 10))
        analogy_entry.pack(side=tk.LEFT, padx=5)

        def _add_analogy():
            concept_pattern = concept_entry.get().strip()
            analogy_text = analogy_entry.get().strip()
            if concept_pattern and analogy_text:
                from ..core.types import CustomAnalogy
                new_analogy = CustomAnalogy(
                    concept_pattern=concept_pattern,
                    analogy=analogy_text,
                    audience="non-technical",
                )
                coach.concepts_file.custom_analogies.append(new_analogy)
                save_concepts_file(coach.config.concepts_path, coach.concepts_file)
                coach.reload_concepts()
                concept_entry.delete(0, tk.END)
                analogy_entry.delete(0, tk.END)
                indicator.set_done("Custom analogy added")

        tk.Button(analogy_frame, text="Add Analogy", command=_add_analogy, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Close button
        tk.Button(dialog, text="Close", command=dialog.destroy, font=("Arial", 10)).pack(pady=10)

    def _save_all():
        """Save concepts and show current status."""
        save_concepts_file(coach.config.concepts_path, coach.concepts_file)
        concepts_label.configure(text=f"Detected: {len(coach.get_detected_concepts())} | Merged: {len(coach.get_merged_concepts())}")
        indicator.set_done("Concepts saved")

    tk.Button(concepts_frame, text="Edit Concepts", command=_open_concepts_editor, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(concepts_frame, text="Save Concepts", command=_save_all, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

    tk.Button(root, text="Ask New Question", command=ask, font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Approve Rule Proposal", command=_approve_pending_rule, font=("Arial", 12)).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12)).pack(pady=5)

    root.after(100, _process_events)
    ask()
    root.mainloop()
