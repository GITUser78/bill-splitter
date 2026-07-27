#!/usr/bin/env bash
# One-time setup for running Bill Splitter inside Termux on Android.
# Termux ships its own precompiled builds of packages that need Rust/C++
# compilation (cryptography, grpcio, watchfiles) — pip's versions fail to
# build or fail to import on Android ARM64, so we install those via pkg
# first and let pip pick up the rest.
set -e

cd "$(dirname "$0")"

pkg update -y
pkg upgrade -y

# tur-repo unlocks precompiled grpcio/watchfiles builds (see below)
pkg install python git libjpeg-turbo python-cryptography tur-repo -y
pkg install python-pillow python-grpcio python-watchfiles -y

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
