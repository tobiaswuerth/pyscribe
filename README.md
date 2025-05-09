I want to live-transcribe meetings by running local text-to-speech AI models.

# Setup (on Windows)

```bash
git clone https://github.com/tobiaswuerth/audio_transcribe.git
cd audio_transcribe
py -m venv .venv
.\.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 # if you want to use CUDA on windows instead of CPU
pip3 install -r .\requirements.txt
```