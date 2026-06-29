from .types import SpeechChunk


class SpeechRecognizer:
    def __init__(self) -> None:
        try:
            import speech_recognition as sr
        except ImportError as exc:
            raise RuntimeError(
                "SpeechRecognition is not installed. Install it with: pip install SpeechRecognition"
            ) from exc

        self.sr = sr
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.75
        self.recognizer.non_speaking_duration = 0.35
        self.recognizer.dynamic_energy_threshold = True

    def calibrate(self, duration: float = 0.6) -> None:
        with self.sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)

    def listen(self) -> str:
        with self.sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except self.sr.UnknownValueError:
            print("Speech was not clear enough to transcribe.")
            return ""
        except self.sr.RequestError as exc:
            raise RuntimeError(f"Speech transcription failed: {exc}") from exc

    def listen_chunk(self, timeout: float, phrase_time_limit: float) -> SpeechChunk:
        with self.sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
            except self.sr.WaitTimeoutError:
                return SpeechChunk(text="", heard_audio=False)

        try:
            text = self.recognizer.recognize_google(audio)
            return SpeechChunk(text=text.strip(), heard_audio=True)
        except self.sr.UnknownValueError:
            return SpeechChunk(text="", heard_audio=True)
        except self.sr.RequestError as exc:
            raise RuntimeError(f"Speech transcription failed: {exc}") from exc
