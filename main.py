import pyaudiowpatch as pyaudio
import time
import wave
import datetime
import re
import os

os.makedirs("recordings", exist_ok=True)
filename = "loopback_record.wav"


def get_available_loopbacks():
    with pyaudio.PyAudio() as p:
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = p.get_device_info_by_index(
            wasapi_info["defaultOutputDevice"]
        )
        devices = [d for d in p.get_loopback_device_info_generator()]

    print(f"Available loopback devices:")
    for di, device in enumerate(devices):
        device["name"] = device["name"].replace("[Loopback]", "").strip()
        default = (
            " <----- DEFAULT" if device["name"] in default_speakers["name"] else ""
        )
        print(f" - {di}: {device['name']}{default}")

    return devices


def select_device():
    while True:
        try:
            device_index = int(input("Select index: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid device index.")

    return device_index


def to_wav(device):
    outdir = "recordings"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = re.sub(r"[^a-zA-Z0-9]", "", device["name"])
    filename = f"{outdir}/rec_{timestamp}_{name}.wav"

    wav = wave.open(filename, "wb")
    wav.setnchannels(device["maxInputChannels"])
    wav.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    wav.setframerate(int(device["defaultSampleRate"]))
    return wav


def main():
    devices = get_available_loopbacks()
    iselected = select_device()
    device = devices[iselected]
    print(f"Selected device index: {iselected} ({device['name']})")

    print("Initializing transcription engine for German language...")
    print(f"Recording audio and transcribing now... (Ctrl+C to stop)")

    with pyaudio.PyAudio() as p:
        with to_wav(device) as wav:

            def callback(in_data, frame_count, time_info, status):
                wav.writeframes(in_data)
                return (in_data, pyaudio.paContinue)

            with p.open(
                format=pyaudio.paInt16,
                channels=device["maxInputChannels"],
                rate=int(device["defaultSampleRate"]),
                input=True,
                input_device_index=device["index"],
                stream_callback=callback,
            ) as _:
                try:
                    while True:
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("Stopping recording and transcription...")


if __name__ == "__main__":
    main()
