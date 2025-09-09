# PyScribe

PyScribe captures audio from Windows loopback devices (system audio/speakers) and uses OpenAI's Whisper model to perform speech recognition locally.

What it can do:
- Generates `.wav` files from system audio output
- Transcribes recordings using [OpenAI's Whisper](https://github.com/openai/whisper) model running locally
- Works without internet connection or API keys

## Use Cases

- **Documentation:** Record and transcribe meetings, lectures, or client calls to create searchable text archives without manual note-taking
- **Content Creation:** Generate subtitles, blog posts, or searchable libraries from podcasts, videos, or educational content
- **Audio Archives:** Convert existing audio recordings into searchable text for better organization and accessibility

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

Additionally, you may also need to install [ffmpeg](https://ffmpeg.org/download.html) and add the `ffmpeg.exe` to the OS PATH variable.

---

## Usage

Adjust [config.yaml](config.yaml) before running.

### a) Record + Transcribe

```bash
py .\record_and_transcribe.py
```

This starts two subsequent tasks:
1. Recorder
   - Records system audio from the configured/selected loopback device, until Ctrl+C
   - Saves recording as `.wav` file
   - Removes silence (useful for better ASR), if configured

2. Transcriber
   - Processes audio file(s) and saves transcription as `.wav.txt`

### b) Individual Actions

For recording only:
```bash
py .\record.py
```

For transcription only:
```bash
py .\transcribe.py
```

## Technical Notes

- The recorder captures system audio output only (loopback devices), not microphone input
- Transcription quality depends on the Whisper model selected in the config file
