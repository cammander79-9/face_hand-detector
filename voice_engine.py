
import pyttsx3
import threading
import queue
from dataclasses import dataclass


@dataclass
class VoiceState:
    running: bool = True
    speaking: bool = False
    current_voice: int = 0
    last_error: str | None = None


class VoiceEngine:
    def __init__(self, rate=175, volume=0.9):
        self.state = VoiceState()
        self._tasks = queue.Queue()
        self._lock = threading.Lock()
        self._ready = threading.Event()
        self._voices = []
        self._rate = rate
        self._volume = volume

        self._worker = threading.Thread(
            target=self._run,
            name="CyberGirlVoice",
            daemon=True,
        )
        self._worker.start()
        self._ready.wait()

        if self.state.last_error:
            raise RuntimeError(self.state.last_error)

    def _run(self):
        engine = None

        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
            engine.setProperty("volume", self._volume)
            self._voices = engine.getProperty("voices")

            if self._voices:
                engine.setProperty("voice", self._voices[0].id)

            self._ready.set()

            while True:
                task = self._tasks.get()

                try:
                    if task is None:
                        break

                    action, value, result = task

                    if action == "speak":
                        self.state.speaking = True
                        engine.say(value)
                        engine.runAndWait()
                        self.state.speaking = False
                        result["ok"] = True

                    elif action == "voice":
                        index = value

                        if not 0 <= index < len(self._voices):
                            raise ValueError(
                                f"Voice index must be between 0 and "
                                f"{len(self._voices) - 1}"
                            )

                        engine.setProperty(
                            "voice", self._voices[index].id
                        )
                        self.state.current_voice = index
                        result["ok"] = True

                    elif action == "stop":
                        engine.stop()
                        result["ok"] = True

                except Exception as exc:
                    self.state.speaking = False
                    self.state.last_error = str(exc)
                    result["error"] = str(exc)

                finally:
                    self._tasks.task_done()
                    if result is not None:
                        result["event"].set()

        except Exception as exc:
            self.state.last_error = str(exc)
            self._ready.set()

        finally:
            self.state.speaking = False
            self.state.running = False
            if engine is not None:
                engine.stop()

    def _submit(self, action, value=None):
        if not self.state.running:
            raise RuntimeError("Voice engine is not running.")

        result = {"event": threading.Event()}
        self._tasks.put((action, value, result))
        result["event"].wait()

        if "error" in result:
            raise RuntimeError(result["error"])

        return result.get("ok", False)

    def speak(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Speech text must be a non-empty string.")
        return self._submit("speak", text)

    def set_voice(self, index):
        return self._submit("voice", index)

    def available_voices(self):
        return [
            {"index": i, "name": voice.name, "id": voice.id}
            for i, voice in enumerate(self._voices)
        ]

    def status(self):
        return {
            "running": self.state.running,
            "speaking": self.state.speaking,
            "current_voice": self.state.current_voice,
            "voice_count": len(self._voices),
            "last_error": self.state.last_error,
        }

    def close(self):
        if self.state.running:
            self._tasks.put(None)
            self._worker.join(timeout=5)


if __name__ == "__main__":
    voice = VoiceEngine()

    try:
        for item in voice.available_voices():
            print(f'{item["index"]}: {item["name"]}')

        voice.speak("Cyber Girl voice system online.")

        if len(voice.available_voices()) > 1:
            voice.set_voice(1)
            voice.speak("Voice changed successfully.")

        print(voice.status())

    finally:
        voice.close()
