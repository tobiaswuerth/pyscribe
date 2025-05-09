import torch
import whisper
from whisper import Whisper


class TranscriptionService:
    def __init__(
        self,
        model_id: str = "large-v3",
        device: str = None,
    ):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Loading Whisper model '{model_id}'...")
        self.model: Whisper = whisper.load_model(model_id, device=device)
        self.device = self.model.device
        self.n_mels = self.model.dims.n_mels
        print(f"Model loaded on device: {self.device}")

    def transcribe(self, audio_path: str, lang="de") -> str:
        return self.model.transcribe(
            audio_path,
            language=lang,
            task="transcribe",
            fp16=self.device.type == "cuda",
            initial_prompt="the person is a swiss professor teaching online school."
        )["text"]


if __name__ == "__main__":
    transcriber = TranscriptionService()

    print("-" * 40)
    audio_file = r"recordings\audio_recording_20250508_201435.wav"
    transcription = transcriber.transcribe(audio_file)

    print("\n--- Transcription Result ---")
    print(transcription)
