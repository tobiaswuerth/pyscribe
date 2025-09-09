import traceback
import torch
import whisper
from whisper import Whisper
import os

from .config import config


class Transcriber:

    def get_todos(self) -> list[str]:
        files = os.listdir(config.save_path)
        audios = [f for f in files if f.endswith(".wav")]
        transcriptions = [f for f in files if f.endswith(".txt")]
        todo = [f for f in audios if f + ".txt" not in transcriptions]
        return todo

    def init_model(self) -> tuple[Whisper, str]:
        print(f"Init Transcription Service with Whisper model '{config.model}' ...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model: Whisper = whisper.load_model(config.model, device=device)
        print(f"Model loaded on device: {device}")
        return model, device

    def transcribe_file(self, audio_path, model, device) -> str:
        print(f"Transcribing file: {audio_path} ...")
        result = model.transcribe(
            audio_path,
            language=config.language,
            initial_prompt=config.prompt,
            fp16=device == "cuda",
            verbose=False,  # shows simple progress bar
            condition_on_previous_text=False,
        )

        return str(result["text"]).strip()

    def save_transcription(self, audio_path: str, transcription: str) -> None:
        out_file = audio_path + ".txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        print(f"Transcription saved to: {out_file}")

    def run(self):
        try:
            todo = self.get_todos()
            if not todo:
                print("No files to transcribe.")
                return

            model, device = self.init_model()

            for audio_file in todo:
                audio_path = os.path.join(config.save_path, audio_file)
                transcription = self.transcribe_file(audio_path, model, device)
                self.save_transcription(audio_path, transcription)

        except KeyboardInterrupt:
            print("Interrupted by user.")
        except Exception as e:
            print(f"Error in Transcriber: {e}")
            traceback.print_exc()
