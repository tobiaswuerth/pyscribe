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

### a) Record + Transcribe simultaneously

```bash
py .\main.py
```

This starts two processes:
1. Recorder
   - Records system audio from the configured/selected loopback device
   - Saves recordings as `.wav` files in segments of configured length (default 5min)

2. Transcriber
   - Monitors output directory for untranscribed audio files
   - Processes files and saves transcription as `.wav.txt`

in the end, by default (depending on config), all individual segments of `.wav` and `.txt` files will be combined into one `.wav` and `.txt` file respectively, and the individual segment files are deleted unless otherwise configured.

### Note on Performance

- Recording and transcribing simultaneously works well for most scenarios
- For highest quality transcription (particularly for longer sessions), consider:
   1. Recording first (using `py .\record.py`)
   2. Transcribing afterwards (using `py .\transcribe.py`)

This sequential approach produces better results because the ASR model has more context and complete sentences when processing the entire audio file, resulting in better transcription quality overall.

### b) Individual Actions

For recording only:
```bash
py .\record.py
```

For transcription only:
```bash
py .\transcribe.py
```

For combining of individual files only:
```bash
py .\combine.py
```


## Technical Notes

- The recorder captures system audio output only (loopback devices), not microphone input
- Transcription quality depends on the Whisper model selected in the config file
- Recording is saved in WAV format with the device's native sample rate
