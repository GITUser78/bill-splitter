# Quick Start Guide

## 1. Get your API key

Sign up at [Google AI Studio](https://aistudio.google.com/apikey) and get your `GOOGLE_API_KEY`.

## 2. Install dependencies

```bash
cd /home/sta/Dokumente/Coding/python/Hello
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Set API key

Either:

```bash
export GOOGLE_API_KEY=...
```

Or create `.env`:

```bash
cp .env.example .env
# Edit .env and add your API key
```

## 4. Run the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The `--host 0.0.0.0` makes it accessible from your phone on the same Wi-Fi.

## 5. Open in browser

```
http://localhost:8000
```

Or from your phone:

```
http://<your-computer-ip>:8000
```

(Find your IP with `hostname -I`)

## 6. Test it

1. **Upload** a restaurant bill photo (or save a sample image from Google Images)
2. Enter your name and submit
3. Share the **QR code** or **link** with another device
4. **Join** from the other device with a different name
5. Both **claim items** you consumed
6. Watch the **totals** update in real-time

## 7. Verify the math

Open the test:

```bash
pytest tests/test_calculations.py -v
```

This verifies the split calculation is correct.

## Troubleshooting

### "No module named pip"

Try:

```bash
python3 -m ensurepip
```

If that fails, your Python needs the venv module:

```bash
apt install python3-venv  # Debian/Ubuntu
```

### "Bill parsing fails"

The receipt photo is blurry or rotated. Try a clearer, straight-on photo.

### "Session not found"

The server was restarted. Sessions are in-memory only. Upload a new bill.

### "Can't access from phone"

Check:
1. Phone and computer on same Wi-Fi
2. Firewall allows port 8000
3. Use your computer's LAN IP, not localhost

Find it:

```bash
hostname -I
```

## What's Next?

- Read [README.md](README.md) for full features and API details
- Read [IMPLEMENTATION.md](IMPLEMENTATION.md) for architecture and code structure
- Modify [app/config.py](app/config.py) to change the Gemini model or polling interval
- Customize [app/static/styles.css](app/static/styles.css) to change colors/fonts

## Project Layout

```
app/main.py              — FastAPI app entry point
app/models.py            — Data models (Participant, Session, etc.)
app/bill_parser.py       — Gemini vision API calls
app/calculations.py      — Split math
app/routes/              — API endpoints
app/templates/           — HTML pages (Jinja2)
app/static/              — CSS and JavaScript
tests/                   — Unit tests
```

Happy splitting! 🍕
