import torch
import whisper
from whisper import Whisper

from transcribe import config


class TranscriptionService:
    def __init__(self):
        print(f"Initializing Transcription Service with Whisper model '{config.model}' ...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model: Whisper = whisper.load_model(config.model, device=device)
        self.device = self.model.device
        self.n_mels = self.model.dims.n_mels
        print(f"Model loaded on device: {self.device}")

    def transcribe(self, audio_path: str) -> str:
        return self.model.transcribe(
            audio_path,
            language=config.language,
            task="transcribe",
            fp16=self.device.type == "cuda",
            initial_prompt=config.initial_prompt,
            verbose=False,
        )["text"]


if __name__ == "__main__":
    transcriber = TranscriptionService()

    print("-" * 40)
    audio_file = r"recordings\rec_20250509_142251_EchoCancellingSpeakerphonePHL49B2U6900CH.wav"
    transcription = transcriber.transcribe(audio_file)

    print("\n--- Transcription Result ---")
    print(transcription)

    out_file = audio_file.replace(".wav", ".txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(transcription)
