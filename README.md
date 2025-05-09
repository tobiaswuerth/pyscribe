# PyScribe

PyScribe captures audio from Windows loopback devices (system audio/speakers) and uses OpenAI's Whisper model to perform speech recognition locally.

What it can do:
- Generates `.wav` files from system audio output
- Transcribes recordings using [OpenAI's Whisper](https://github.com/openai/whisper) model running locally
- Works without internet connection or API keys

### Use Cases
- Meeting Documentation - Record and transcribe team meetings, brainstorming sessions, or client calls to create searchable text archives without manual note-taking.
- Content Creator Workflow - Transcribe podcasts, videos, or lectures automatically to generate subtitles, repurpose content for blog posts, or create searchable libraries.
- Audio Archive Processing - Convert existing audio recordings into searchable text.
- Education - Transcribe lectures or educational content from media players.

---

## Setup

```bash
git clone https://github.com/tobiaswuerth/pyscribe.git
cd pyscribe
py -m venv .venv
.\.venv\Scripts\activate
python.exe -m pip install --upgrade pip

# For CUDA-enabled GPUs
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 

pip3 install -r .\requirements.txt
```
---

## Usage

Adjust [config.yaml](config.yaml) before running.

### a) Record + Transcribe simultaneously

```bash
py .\main.py
```

This starts two processes:
1. Recorder
   - Records audio from the configured/selected loopback device (system audio)
   - Saves recordings as `.wav` files in segments of configured length (default 60 seconds)

2. Transcriber
   - Monitors output directory for untranscribed audio files
   - Processes files and saves transcription as `.wav.txt`

### b) Record or Transcribe individually

For recording only:
```bash
py .\record.py
```

For transcription only:
```bash
py .\transcribe.py
```

Note: When using `record.py`, it creates a single continuous file rather than segmented recordings. The `transcribe.py` script processes all untranscribed files in the output directory.

## Technical Notes

- The recorder captures system audio output only (loopback devices), not microphone input
- Transcription quality depends on the Whisper model selected in the config file
- Recording is saved in WAV format with the device's native sample rate
