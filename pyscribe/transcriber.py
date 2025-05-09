import multiprocessing as mp
import traceback
import torch
import whisper
from whisper import Whisper
import os
import time

from .config import config


class Transcriber(mp.Process):
    def __init__(self, on_exit: mp.Event):
        super().__init__()
        self.on_exit: mp.Event = on_exit

    def initialize(self):
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
            initial_prompt=config.prompt,
            # verbose=False, # show progress bar
        )["text"]

    def get_files_todo(self) -> list[str]:
        files = os.listdir(config.save_path)
        audios = [f for f in files if f.endswith(".wav")]
        transcriptions = [f for f in files if f.endswith(".txt")]
        todo = [f for f in audios if f + ".txt" not in transcriptions]
        return todo

    def process_audio_file(self, filename: str) -> None:
        audio_path = os.path.join(config.save_path, filename)
        transcription = self.transcribe(audio_path)

        out_file = audio_path + ".txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(transcription)

        print(f"🗣: {transcription}")

    def process_directory(self) -> bool:
        todo = self.get_files_todo()
        if not todo:
            return False

        for audio_file in todo:
            self.process_audio_file(audio_file)
        return True

    def run(self):
        try:
            self.initialize()

            while not self.on_exit.is_set():
                did_work = self.process_directory()
                if not did_work:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("Interrupted by user.")
            if config.finish_processing_on_exit:
                print("Finishing processing remaining files...")
                _itercount = 0
                while True:
                    tmp_files = [f for f in os.listdir(config.save_path) if f.endswith(".tmp")]
                    if not tmp_files:
                        break
                    time.sleep(.5)
                    _itercount += 1
                    if _itercount > 10:
                        print("Timeout waiting for tmp files to finish.")
                        return
                self.process_directory()
        except Exception as e:
            print(f"Error in Transcriber: {e}")
            traceback.print_exc()
        finally:
            self.on_exit.set()
            print("Transcriber process finished.")
