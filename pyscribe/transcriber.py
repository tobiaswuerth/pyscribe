import traceback
import torch
import whisper
from whisper import Whisper
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

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

    def remove_silence(self, audio_path: str) -> str:
        if not config.remove_silence:
            return audio_path

        print(f"Removing silence from: {audio_path} ...")
        new_path = audio_path.replace(".wav", ".silence_removed.wav")
        sound = AudioSegment.from_file(audio_path, format="wav")
        chunks = split_on_silence(sound, silence_thresh=-40)
        
        combined = AudioSegment.empty()
        for chunk in chunks:
            combined += chunk
        
        combined.export(new_path, format="wav")
        os.rename(audio_path, audio_path + ".backup")

        print(f"Silence removed audio saved to: {new_path}")
        return new_path

    def transcribe_file(self, audio_path, model:Whisper, device) -> str:
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
                audio_path = self.remove_silence(audio_path)
                transcription = self.transcribe_file(audio_path, model, device)
                self.save_transcription(audio_path, transcription)

        except KeyboardInterrupt:
            print("Interrupted by user.")
        except Exception as e:
            print(f"Error in Transcriber: {e}")
            traceback.print_exc()
