#!/usr/bin/env bash
# One-time environment setup for a fresh session. Run from the repo root.
set -e
pip install --break-system-packages -q kokoro-onnx soundfile numpy pillow
mkdir -p tts ~/.fonts
[ -f tts/kokoro.onnx ] || curl -sSL -o tts/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f tts/voices.bin ] || curl -sSL -o tts/voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
[ -f ~/.fonts/PlayfairDisplay.ttf ] || curl -sSL -o ~/.fonts/PlayfairDisplay.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf"
[ -f ~/.fonts/PlayfairSC-Black.ttf ] || curl -sSL -o ~/.fonts/PlayfairSC-Black.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplaysc/PlayfairDisplaySC-Black.ttf"
fc-cache -f >/dev/null
which rsvg-convert ffmpeg >/dev/null && echo "setup ok"
