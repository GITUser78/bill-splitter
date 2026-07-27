#!/usr/bin/env bash
# One-time setup for running Bill Splitter inside Termux on Android.
# Some dependencies need Rust/C++ toolchains to build from source, which
# don't work out of the box on Android:
#   - cryptography, pillow: Termux ships precompiled apt (pkg) packages
#   - grpcio, watchfiles: no apt package exists; TUR hosts prebuilt wheels
#     via its own pip index instead
set -e

cd "$(dirname "$0")"

pkg update -y
pkg upgrade -y

pkg install python git libjpeg-turbo python-cryptography python-pillow -y

pip install --extra-index-url https://termux-user-repository.github.io/pypi/ grpcio watchfiles

pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo
  echo "Created .env — edit it and add your Gemini API key:"
  echo "  GOOGLE_API_KEY=your_google_gemini_api_key_here"
  echo "Get one at https://aistudio.google.com/apikey"
else
  echo ".env already exists, leaving it as-is."
fi

echo
echo "Setup complete. Run ./start-termux.sh to launch the app."
