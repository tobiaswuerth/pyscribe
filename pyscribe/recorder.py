import pyaudiowpatch as pyaudio
import os
import traceback
import wave
import datetime
import re
import time

from .config import config


class Recorder:
    def prepare_recording_device(self):
        with pyaudio.PyAudio() as p:
            devices = [d for d in p.get_loopback_device_info_generator()]
        assert devices, "No loopback devices found."

        if config.default_device:
            device = next(
                (d for d in devices if config.default_device in d["name"]),
                None,
            )
            assert device, f"Device '{config.default_device}' not found."
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

            device = devices[device_index]

        print(f"Recording from device: {device['name']}")
        return device

    def prepare_wav(self, device) -> tuple[wave.Wave_write, str]:
        if config.save_path:
            print(f"Saving recordings to: {config.save_path}")
            os.makedirs(config.save_path, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = re.sub(r"[^a-zA-Z0-9]", "", device["name"])
        filename = f"rec_{timestamp}_{name}.wav.tmp"
        filename = os.path.join(config.save_path, filename)

        wav = wave.open(filename, "wb")
        wav.setnchannels(device["maxInputChannels"])
        wav.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wav.setframerate(int(device["defaultSampleRate"]))
        return wav, filename

    def record(self, wav: wave.Wave_write, device):
        def audio_stream_callback(in_data, frame_count, time_info, status):
            wav.writeframes(in_data)
            return in_data, pyaudio.paContinue

        try:
            print(f"Recording starting now, press Ctrl+C to stop...")
            with pyaudio.PyAudio() as p:
                with p.open(
                    format=pyaudio.paInt16,
                    channels=device["maxInputChannels"],
                    rate=int(device["defaultSampleRate"]),
                    input=True,
                    frames_per_buffer=1024,
                    input_device_index=device["index"],
                    stream_callback=audio_stream_callback,
                ) as stream:
                    while True:
                        time.sleep(0.1)
        except KeyboardInterrupt:
            print("Interrupted by user.")
        except Exception as e:
            print(f"Error in Recorder: {e}")
            traceback.print_exc()

    def run(self):
        device = self.prepare_recording_device()

        wav, filename = self.prepare_wav(device)
        self.record(wav, device)
        wav.close()

        fix_name = filename.replace(".tmp", "")
        os.rename(filename, fix_name)
