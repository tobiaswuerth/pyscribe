Can be used to record and/or transcribe audio on Windows.

The recording generates `.wav` files for a given loopback device.
The transcription is done by running [OpenAI's Whisper](https://github.com/openai/whisper) model locally for ASR (Automatic Speech Recognition).

---

# Setup
on Windows

```bash
git clone https://github.com/tobiaswuerth/audio_transcribe.git
cd audio_transcribe
py -m venv .venv
.\.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 # if you want to use CUDA on Windows instead of CPU
pip3 install -r .\requirements.txt
```

---

# Usage

Adjust [config.yaml](config.yaml) if desired.

### a) Record + Transcribe simultaneously
run
```bash
py .\main.py
```

This will start two processes:
1. Recorder
    - records the configured/selected audio device continuously (until Ctrl+C)
    - saves the recordings to .wav files of configured segment length (e.g. 60 seconds each)
2. Transcriber
    - monitors output directory for unprocessed audio files (`.wav`)
    - transcribes files and saves transcription to `.wav.txt`

### b) Record or Transcribe individually
run

```bash
py .\record.py
```
or

```bash
py .\transcribe.py
```
individually to just record or transcribe.

Note: The recorder is setup to overwrite the default `segment_duration` in the config file for this case to produce just one long file.
Transcribe will process all files which are not transcribed yet available in the `save_path` directory.