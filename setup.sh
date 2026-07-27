#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip -q
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
echo "Setup complete. Run ./start.sh to launch the app."
