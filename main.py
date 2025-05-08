"""A simple example of recording from speakers ('What you hear') using the WASAPI loopback device with live transcription"""

import pyaudiowpatch as pyaudio
import time
import wave
import datetime
import re
import os
import numpy as np
from faster_whisper import WhisperModel
import threading
import queue
from collections import deque

CHUNK_SIZE = 1024
SAMPLE_RATE = 16000  # Whisper model uses 16kHz
SEGMENT_DURATION = 2  # Process 2 seconds of audio at a time

os.makedirs("recordings", exist_ok=True)
filename = "loopback_record.wav"

model_size = "large-v3"  # Options: tiny, base, small, medium, large
model = WhisperModel(model_size, device="cuda", compute_type="int8")

audio_queue = queue.Queue()
audio_buffer = deque(maxlen=int(SAMPLE_RATE * SEGMENT_DURATION))


def audio_processor():
    """Process audio chunks in a separate thread"""
    while True:
        if audio_queue.empty():
            time.sleep(0.1)
            continue

        print(len(audio_queue.queue), end="\r")
        audio_chunk = audio_queue.get()
        if len(audio_chunk) == 0:
            continue

        audio_array = np.array(audio_chunk).astype(np.float32) / 32768.0
        segments, _ = model.transcribe(
            audio_array,
            language="en"
        )
        transcription = " ".join([segment.text for segment in segments])

        if transcription:
            print(f"🗣: {transcription}")

        audio_queue.task_done()


transcription_thread = threading.Thread(target=audio_processor, daemon=True)
transcription_thread.start()


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

    # Track accumulated frames and time
    frames_accumulated = 0
    sample_rate = int(device["defaultSampleRate"])
    samples_per_segment = int(SEGMENT_DURATION * sample_rate)
    chunk_samples = []

    with pyaudio.PyAudio() as p:
        with to_wav(device) as wav:

            def callback(in_data, frame_count, time_info, status):
                nonlocal frames_accumulated, chunk_samples

                wav.writeframes(in_data)

                # Convert the audio data for processing
                audio_data = np.frombuffer(in_data, dtype=np.int16)
                chunk_samples.extend(audio_data.tolist())
                frames_accumulated += frame_count

                # Check if we have 2 seconds of audio
                if frames_accumulated >= samples_per_segment:
                    # Resample to 16kHz for Whisper if needed
                    if sample_rate != SAMPLE_RATE:
                        resampling_factor = SAMPLE_RATE / sample_rate
                        resampled = np.array(
                            [
                                chunk_samples[int(i / resampling_factor)]
                                for i in range(
                                    int(len(chunk_samples) * resampling_factor)
                                )
                            ]
                        )
                        audio_queue.put(resampled)
                    else:
                        audio_queue.put(chunk_samples)

                    # Reset for next chunk
                    frames_accumulated = 0
                    chunk_samples = []

                return (in_data, pyaudio.paContinue)

            with p.open(
                format=pyaudio.paInt16,
                channels=device["maxInputChannels"],
                rate=int(device["defaultSampleRate"]),
                frames_per_buffer=CHUNK_SIZE,
                input=True,
                input_device_index=device["index"],
                stream_callback=callback,
            ) as stream:
                try:
                    while True:
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("Stopping recording and transcription...")
                    # Wait for the remaining audio to be processed
                    if chunk_samples:
                        audio_queue.put(chunk_samples)
            audio_queue.join()


if __name__ == "__main__":
    main()
