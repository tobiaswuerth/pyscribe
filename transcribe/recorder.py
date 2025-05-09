import multiprocessing as mp
import pyaudiowpatch as pyaudio
import os
import traceback
import wave
import datetime
import re
import atexit
import time

from .config import config


class Recorder(mp.Process):
    def __init__(self, on_exit: mp.Event):
        super().__init__()
        self.on_exit: mp.Event = on_exit
        self.is_initialized = False

        atexit.register(self.finalize_wav)

    def initialize(self):
        self.prepare_recording_device()
        self.prepare_saving()
        self.is_initialized = True

    def prepare_recording_device(self):
        with pyaudio.PyAudio() as p:
            devices = [d for d in p.get_loopback_device_info_generator()]
        assert devices, "No loopback devices found."

        if config.default_device:
            self.device = next(
                (d for d in devices if config.default_device in d["name"]),
                None,
            )
            assert self.device, f"Device '{config.default_device}' not found."
        else:
            print(f"Available loopback devices:")
            for di, device in enumerate(devices):
                device["name"] = device["name"].replace("[Loopback]", "").strip()
                print(f" - {di}: {device['name']}")

            while True:
                try:
                    device_index = input("Select index: ")
                    device_index = int(device_index)
                    if 0 > device_index >= len(devices):
                        print("Invalid index. Please select a valid device index.")
                        continue
                    break
                except Exception:
                    print("Invalid input. Please enter a valid device index.")
                    continue

            self.device = devices[device_index]

        print(f"Recording from device: {self.device['name']}")

    def prepare_saving(self):
        if config.save_path:
            os.makedirs(config.save_path, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = re.sub(r"[^a-zA-Z0-9]", "", self.device["name"])
        filename = f"rec_{timestamp}_{name}"
        filename += "_{counter}_WIP.wav"
        self._filename = os.path.join(config.save_path, filename)

        self.wav = None
        self.file_counter = -1
        self.recording_started_at = None

    @property
    def filename(self):
        return self._filename.format(counter=f"{self.file_counter:03d}")

    def new_wav_file(self):
        self.file_counter += 1
        wav = wave.open(self.filename, "wb")
        wav.setnchannels(self.device["maxInputChannels"])
        wav.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wav.setframerate(int(self.device["defaultSampleRate"]))
        return wav

    def finalize_wav(self):
        if self.wav:
            self.wav.close()
            self.wav = None
            final_name = self.filename.replace("_WIP", "")
            os.rename(self.filename, final_name)

    def audio_stream_callback(self, in_data, frame_count, time_info, status):
        if self.wav is None:
            self.wav = self.new_wav_file()
            self.recording_started_at = time_info["current_time"]

        self.wav.writeframes(in_data)

        rec_duration = time_info["current_time"] - self.recording_started_at
        if rec_duration >= config.segment_duration:
            self.finalize_wav()

        return in_data, pyaudio.paContinue

    def run(self):
        try:
            assert self.is_initialized, "Recorder not initialized."

            print(f"Recording now started, press Ctrl+C to stop...")
            with pyaudio.PyAudio() as p:
                with p.open(
                    format=pyaudio.paInt16,
                    channels=self.device["maxInputChannels"],
                    rate=int(self.device["defaultSampleRate"]),
                    input=True,
                    frames_per_buffer=1024,
                    input_device_index=self.device["index"],
                    stream_callback=self.audio_stream_callback,
                ) as _:
                    while not self.on_exit.is_set():
                        time.sleep(0.1)

        except KeyboardInterrupt:
            print("Interrupted by user.")
        except Exception as e:
            print(f"Error in Recorder: {e}")
            traceback.print_exc()
        finally:
            self.on_exit.set()
            self.finalize_wav()
            print("Recorder process finished.")
