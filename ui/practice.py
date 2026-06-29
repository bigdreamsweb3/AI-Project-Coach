import queue
import threading
import time
import tkinter as tk
from tkinter import scrolledtext
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

    indicator = ListeningIndicator(root)
    indicator.pack(fill=tk.X, padx=10, pady=(10, 0))

    text_area = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        width=100,
        height=30,
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

        append_plain(text_area, "\nQuestion\n", "label")
        append_markdown(text_area, practice_question.question)
        if practice_question.model_answer:
            append_plain(text_area, "\nModel Answer\n", "label")
            append_markdown(text_area, practice_question.model_answer)
        append_plain(text_area, "\nYour Answer\n", "label")
        append_observation(
            coach.config.observation_log_path,
            mode="Practice Question",
            project_name=coach.config.project_name,
            question=practice_question.question,
            guidance="Practice question generated. The speaker should answer with enough project-specific context before capture.",
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
                    coach.config.observation_log_path,
                    mode="Practice Answer",
                    project_name=coach.config.project_name,
                    question=current_question["text"],
                    guidance="Answer captured after passing the local meaningful-context check.",
                    answer=str(payload),
                )
            elif event == "need_more":
                indicator.set_silence(str(payload))
            elif event == "error":
                indicator.set_error(str(payload))

        root.after(100, _process_events)

    def _show_rule_proposals(question: str, guidance: str) -> None:
        pending_rule_proposals.clear()
        pending_rule_proposals.extend(
            propose_rules_from_observation(question, guidance, coach.config.project_rules)
        )

        if not pending_rule_proposals:
            return

        append_plain(text_area, "\nRule Proposal\n", "label")
        for proposal in pending_rule_proposals:
            append_plain(text_area, f"{proposal.title}\n{proposal.reason}\n{proposal.rule_text}\n")
            append_rule_proposal(
                coach.config.rule_proposals_path,
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

    tk.Button(root, text="Ask New Question", command=ask, font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Approve Rule Proposal", command=_approve_pending_rule, font=("Arial", 12)).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12)).pack(pady=5)

    root.after(100, _process_events)
    ask()
    root.mainloop()
