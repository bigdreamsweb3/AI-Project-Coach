import queue
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import TYPE_CHECKING

from ..coaching.cue_coach import cue_matches_spoken_text, extract_cues
from ..coaching.rule_proposals import propose_rules_from_observation
from ..core.constants import (
    LIVE_DONE_AFTER_SILENCE_SECONDS,
    LIVE_LISTEN_TIMEOUT_SECONDS,
    LIVE_PHRASE_TIME_LIMIT_SECONDS,
    LIVE_WINDOW_GEOMETRY,
    LIVE_WINDOW_TITLE,
)
from ..core.types import AudienceType
from ..observations.log import append_observation
from ..observations.rule_proposals import append_rule_proposal
from .listening_indicator import ListeningIndicator
from .text_format import configure_rich_text

if TYPE_CHECKING:
    from ..app import TrustLinkCoach


class LiveInterviewUi:
    def __init__(self, coach: "TrustLinkCoach") -> None:
        self.coach = coach
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.listening = False
        self.listen_thread: threading.Thread | None = None
        self.generation_thread: threading.Thread | None = None
        self.generation_id = 0
        self.last_generated_transcript = ""
        self.pending_generation = False
        self.pending_generation_final = False
        self.transcript_parts: list[str] = []
        self.speaker_parts: list[str] = []
        self.cues: list[str] = []
        self.active_cue_index = 0
        self.coaching_speaker = False
        self.logged_answer_completion = False
        self.last_audio_at = 0.0
        self.marked_done = False

        self.root = tk.Tk()
        self.root.title(LIVE_WINDOW_TITLE)
        self.root.geometry(LIVE_WINDOW_GEOMETRY)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.coach.config.live_window_alpha)

        self.status = tk.StringVar(value="Ready")
        self.model_status = tk.StringVar(value=f"AI models: {self.coach.ai.active_models_label()}")
        self.indicator: ListeningIndicator
        self.transcript_text: scrolledtext.ScrolledText
        self.answer_text: scrolledtext.ScrolledText
        self.start_button: tk.Button
        self.stop_button: tk.Button

        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def run(self) -> None:
        self.root.after(100, self._process_events)
        self.root.mainloop()

    def _build_layout(self) -> None:
        container = tk.Frame(self.root, padx=12, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        status_label = tk.Label(
            container,
            textvariable=self.status,
            anchor="w",
            font=("Arial", 13, "bold"),
        )
        status_label.pack(fill=tk.X, pady=(0, 10))

        model_label = tk.Label(
            container,
            textvariable=self.model_status,
            anchor="w",
            font=("Arial", 10),
        )
        model_label.pack(fill=tk.X, pady=(0, 5))

        # Audience switcher
        audience_frame = tk.Frame(container)
        audience_frame.pack(fill=tk.X, pady=(0, 10))

        self.audience_status = tk.StringVar(value=f"Audience: {self.coach.get_audience().value}")

        def on_audience_change(event):
            selected = self.audience_var.get()
            for aud in AudienceType:
                if aud.value == selected:
                    self.coach.set_audience(aud)
                    self.audience_status.set(f"Audience: {aud.value}")
                    break

        tk.Label(audience_frame, text="Audience:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.audience_var = tk.StringVar(value=self.coach.get_audience().value)
        self.audience_combo = ttk.Combobox(
            audience_frame,
            textvariable=self.audience_var,
            values=[a.value for a in AudienceType],
            state="readonly",
            width=15,
            font=("Arial", 10),
        )
        self.audience_combo.pack(side=tk.LEFT, padx=5)
        self.audience_combo.bind("<<ComboboxSelected>>", on_audience_change)

        self.indicator = ListeningIndicator(container)
        self.indicator.pack(fill=tk.X, pady=(0, 10))

        columns = tk.Frame(container)
        columns.pack(fill=tk.BOTH, expand=True)
        columns.columnconfigure(0, weight=1)
        columns.columnconfigure(1, weight=1)
        columns.rowconfigure(1, weight=1)

        tk.Label(columns, text="Interview Transcript", anchor="w", font=("Arial", 11, "bold")).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6),
        )
        tk.Label(columns, text="Suggested Answer", anchor="w", font=("Arial", 11, "bold")).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

        self.transcript_text = scrolledtext.ScrolledText(
            columns,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=28,
        )
        self.transcript_text.grid(row=1, column=0, sticky="nsew", padx=(0, 6))

        self.answer_text = scrolledtext.ScrolledText(
            columns,
            wrap=tk.WORD,
            font=("Georgia", 11),
            height=28,
        )
        self.answer_text.grid(row=1, column=1, sticky="nsew", padx=(6, 0))
        configure_rich_text(self.answer_text)
        self.answer_text.tag_configure("cue_done", foreground="#64748b", font=("Georgia", 11))
        self.answer_text.tag_configure("cue_active", foreground="#166534", background="#dcfce7", font=("Georgia", 12, "bold"), spacing3=5)
        self.answer_text.tag_configure("cue_pending", foreground="#273043", font=("Georgia", 11), spacing3=4)

        controls = tk.Frame(container)
        controls.pack(fill=tk.X, pady=(12, 0))

        self.start_button = tk.Button(
            controls,
            text="Start Listening",
            command=self._start_listening,
            font=("Arial", 12),
            width=16,
        )
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(
            controls,
            text="Stop",
            command=self._stop_listening,
            font=("Arial", 12),
            width=10,
            state=tk.DISABLED,
        )
        self.stop_button.pack(side=tk.LEFT, padx=(8, 0))

        tk.Button(
            controls,
            text="Clear",
            command=self._clear,
            font=("Arial", 12),
            width=10,
        ).pack(side=tk.LEFT, padx=(8, 0))

        tk.Button(
            controls,
            text="Exit",
            command=self.root.quit,
            font=("Arial", 12),
            width=10,
        ).pack(side=tk.RIGHT)

    def _start_listening(self) -> None:
        if self.listening:
            return

        self.listening = True
        self.marked_done = False
        self.last_audio_at = time.monotonic()
        self.status.set("Calibrating microphone...")
        self.indicator.set_listening("Calibrating microphone")
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)

        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

    def _stop_listening(self) -> None:
        self.listening = False
        self.status.set("Stopped")
        self.indicator.set_idle("Stopped")
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)

    def _clear(self) -> None:
        self.generation_id += 1
        self.transcript_parts.clear()
        self.speaker_parts.clear()
        self.cues.clear()
        self.active_cue_index = 0
        self.coaching_speaker = False
        self.logged_answer_completion = False
        self.last_generated_transcript = ""
        self.pending_generation = False
        self.pending_generation_final = False
        self.marked_done = False
        self.transcript_text.delete("1.0", tk.END)
        self.answer_text.delete("1.0", tk.END)
        self.status.set("Ready")
        self.indicator.set_idle("Ready")

    def _close(self) -> None:
        self.listening = False
        self.root.destroy()

    def _listen_loop(self) -> None:
        try:
            self.coach.speech.calibrate()
            self.events.put(("status", "Listening..."))

            while self.listening:
                chunk = self.coach.speech.listen_chunk(
                    timeout=LIVE_LISTEN_TIMEOUT_SECONDS,
                    phrase_time_limit=LIVE_PHRASE_TIME_LIMIT_SECONDS,
                )

                now = time.monotonic()
                if chunk.heard_audio:
                    self.last_audio_at = now
                    self.marked_done = False
                    self.events.put(("status", "Talking detected"))
                    if chunk.text:
                        self.events.put(("transcript", chunk.text))
                    continue

                if self.transcript_parts and now - self.last_audio_at >= LIVE_DONE_AFTER_SILENCE_SECONDS:
                    if not self.marked_done:
                        self.marked_done = True
                        self.events.put(("done", None))
                    continue

                self.events.put(("status", "Listening for speech..."))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def _process_events(self) -> None:
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break

            if event == "status":
                self.status.set(str(payload))
                if payload == "Talking detected":
                    self.indicator.set_talking("Speech detected")
                elif payload == "Listening for speech...":
                    self.indicator.set_silence("Waiting for speech")
                elif payload == "Listening...":
                    self.indicator.set_listening("Listening")
            elif event == "transcript":
                self._append_transcript(str(payload))
            elif event == "speaker_transcript":
                self._append_speaker_transcript(str(payload))
            elif event == "answer":
                generation_id, answer, is_final = payload  # type: ignore[misc]
                self._show_answer(int(generation_id), str(answer), bool(is_final))
            elif event == "done":
                self.status.set("Question finished. Finalizing answer...")
                self.indicator.set_done("Question finished")
                self._request_generation(is_final=True, force=True)
            elif event == "error":
                self.status.set(f"Error: {payload}")
                self.indicator.set_error(str(payload))

        self.root.after(100, self._process_events)

    def _append_transcript(self, text: str) -> None:
        if self.coaching_speaker:
            self._append_speaker_transcript(text)
            return

        self.transcript_parts.append(text)
        self.transcript_text.insert(tk.END, f"{text} ")
        self.transcript_text.see(tk.END)
        self.status.set("Talking detected. Drafting answer...")
        self.indicator.set_talking("Speech detected")
        self._request_generation(is_final=False)

    def _append_speaker_transcript(self, text: str) -> None:
        self.speaker_parts.append(text)
        self.transcript_text.insert(tk.END, f"\nYou: {text} ")
        self.transcript_text.see(tk.END)
        self.status.set("Coaching your answer. Follow the green cue.")
        self.indicator.set_talking("Listening to your answer")
        self._advance_cues(text)

    def _request_generation(self, is_final: bool, force: bool = False) -> None:
        transcript = self._transcript()
        if not transcript:
            return

        should_generate_first_draft = not self.last_generated_transcript
        new_chars = len(transcript) - len(self.last_generated_transcript)
        if not force and not should_generate_first_draft and new_chars < self.coach.config.live_regenerate_after_chars:
            return

        if self.generation_thread and self.generation_thread.is_alive():
            self.pending_generation = True
            self.pending_generation_final = self.pending_generation_final or is_final
            return

        self.generation_id += 1
        generation_id = self.generation_id
        self.last_generated_transcript = transcript
        self.pending_generation = False
        self.pending_generation_final = False
        self.answer_text.delete("1.0", tk.END)
        self.answer_text.insert(tk.END, "Generating answer...")

        self.generation_thread = threading.Thread(
            target=self._generate_answer,
            args=(generation_id, transcript, is_final),
            daemon=True,
        )
        self.generation_thread.start()

    def _generate_answer(self, generation_id: int, transcript: str, is_final: bool) -> None:
        try:
            answer = self.coach.generate_live_cues(
                transcript,
                self.coach.config.live_context_chars,
                self.coach.config.project_rules,
                is_final=is_final,
            )
            self.events.put(("answer", (generation_id, answer, is_final)))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def _show_answer(self, generation_id: int, answer: str, is_final: bool) -> None:
        if generation_id != self.generation_id:
            return

        self.cues = extract_cues(answer)
        self.active_cue_index = 0
        self.logged_answer_completion = False
        self._render_cues()
        self.model_status.set(f"AI models: {self.coach.ai.active_models_label()} | Last used: {self.coach.ai.last_model_label()}")
        self.coaching_speaker = is_final
        self.status.set("Answer cues ready. Follow the green cue." if is_final else "Draft cues ready. Still listening...")
        if is_final:
            guidance = "Live answer cues generated in systems-language style. The speaker should follow the green NEXT cue while explaining in their own words—concepts, not code."
            append_observation(
                self.coach.config.observations_path,
                mode="Live Interview Cues",
                project_name=self.coach.config.project_name,
                question=self._transcript(),
                guidance=guidance,
                answer="\n".join(self.cues),
            )
            try:
                for proposal in propose_rules_from_observation(
                    self.coach.ai,
                    self.coach.config.project_name,
                    self.coach.knowledge,
                    self._transcript(),
                    guidance,
                    self.coach.config.project_rules,
                    self.coach.config.live_context_chars,
                    self.coach.config.proposal_max_tokens,
                ):
                    append_rule_proposal(
                        self.coach.config.improvement_proposals_path,
                        mode="Live Interview Cues",
                        question=self._transcript(),
                        proposal=proposal,
                    )
                self.model_status.set(
                    f"AI models: {self.coach.ai.active_models_label()} | Last used: {self.coach.ai.last_model_label()}"
                )
            except Exception as exc:
                self.status.set(f"Proposal review failed: {exc}")

        if self.pending_generation:
            pending_final = self.pending_generation_final
            self._request_generation(is_final=pending_final, force=True)

    def _advance_cues(self, spoken_text: str) -> None:
        if not self.cues or self.active_cue_index >= len(self.cues):
            return

        active_cue = self.cues[self.active_cue_index]
        if cue_matches_spoken_text(active_cue, spoken_text):
            self.active_cue_index += 1
            self._render_cues()
            if self.active_cue_index >= len(self.cues) and not self.logged_answer_completion:
                self.logged_answer_completion = True
                append_observation(
                    self.coach.config.observations_path,
                    mode="Live Answer Complete",
                    project_name=self.coach.config.project_name,
                    question=self._transcript(),
                    guidance="Speaker moved through every cue using local speech tracking.",
                    answer=" ".join(self.speaker_parts),
                )

    def _render_cues(self) -> None:
        self.answer_text.delete("1.0", tk.END)
        if not self.cues:
            self.answer_text.insert(tk.END, "No cues generated.", "body")
            return

        for index, cue in enumerate(self.cues):
            if index < self.active_cue_index:
                marker = "DONE: "
                tag = "cue_done"
            elif index == self.active_cue_index:
                marker = "NEXT: "
                tag = "cue_active"
            else:
                marker = "- "
                tag = "cue_pending"

            self.answer_text.insert(tk.END, f"{marker}{cue}\n", tag)
        self.answer_text.see(tk.END)

    def _transcript(self) -> str:
        return " ".join(self.transcript_parts).strip()


def run_live_interview_ui(coach: "TrustLinkCoach") -> None:
    LiveInterviewUi(coach).run()
