import tkinter as tk


class ListeningIndicator:
    def __init__(self, parent: tk.Widget) -> None:
        self.frame = tk.Frame(parent)
        self.canvas = tk.Canvas(self.frame, width=24, height=24, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT)
        self.label_var = tk.StringVar(value="Idle")
        self.label = tk.Label(self.frame, textvariable=self.label_var, anchor="w", font=("Georgia", 11, "bold"))
        self.label.pack(side=tk.LEFT, padx=(6, 0))

        self.state = "idle"
        self.pulse_on = False
        self.after_id: str | None = None
        self._draw("#9aa4b2", 7)

    def pack(self, **kwargs) -> None:
        self.frame.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        self.frame.grid(**kwargs)

    def set_idle(self, text: str = "Idle") -> None:
        self._set_state("idle", text)

    def set_listening(self, text: str = "Listening") -> None:
        self._set_state("listening", text)

    def set_talking(self, text: str = "Speech detected") -> None:
        self._set_state("talking", text)

    def set_silence(self, text: str = "Waiting after silence") -> None:
        self._set_state("silence", text)

    def set_done(self, text: str = "Speech finished") -> None:
        self._set_state("done", text)

    def set_error(self, text: str) -> None:
        self._set_state("error", text)

    def _set_state(self, state: str, text: str) -> None:
        self.state = state
        self.label_var.set(text)
        if self.after_id is None:
            self._pulse()

    def _pulse(self) -> None:
        color, base_radius = {
            "idle": ("#9aa4b2", 7),
            "listening": ("#2f80ed", 7),
            "talking": ("#22a06b", 9),
            "silence": ("#f59e0b", 7),
            "done": ("#64748b", 7),
            "error": ("#dc2626", 7),
        }.get(self.state, ("#9aa4b2", 7))

        radius = base_radius + (3 if self.pulse_on and self.state in {"listening", "talking"} else 0)
        self._draw(color, radius)
        self.pulse_on = not self.pulse_on
        self.after_id = self.frame.after(280, self._pulse)

    def _draw(self, color: str, radius: int) -> None:
        self.canvas.delete("all")
        center = 12
        self.canvas.create_oval(center - radius, center - radius, center + radius, center + radius, fill=color, outline="")
