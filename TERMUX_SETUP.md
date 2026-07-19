# Hosting on Android via Termux (No Cloud, No Laptop)

Run the whole app on the phone that's collecting the bill. Guests join over
your phone's Wi-Fi hotspot — no internet needed on their end, no server to
pay for or maintain.

**How it works:** Android's personal hotspot shares your cellular data, it
doesn't replace it. So your phone keeps internet access (needed for the
Gemini vision call when you upload the bill photo) while also acting as a
local Wi-Fi network that guests join to reach the app.

This is a one-time setup, followed by a short routine you repeat each time
you use the app.

---

## One-Time Setup

### 1. Install Termux

Install Termux from **F-Droid**, not the Play Store — the Play Store build
is outdated and its package repos no longer work.

- F-Droid: https://f-droid.org/packages/com.termux/

### 2. Install system packages

Open Termux and run:

```bash
pkg update
pkg install python git libjpeg-turbo
```

`libjpeg-turbo` lets Pillow's image resizing work without a slow from-source
build.

### 3. Clone the repo

```bash
git clone https://github.com/GITUser78/bill-splitter.git
cd bill-splitter
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

If `Pillow` fails to build, install Termux's precompiled version instead and
remove it from `requirements.txt` for this device:

```bash
pkg install python-pillow
```

### 5. Set your Gemini API key

```bash
cp .env.example .env
```

Edit `.env` and paste your key:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 6. Test it once

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in the phone's browser to confirm it loads,
then `Ctrl+C` to stop it.

---

## At the Restaurant (Every Time)

### 1. Turn on your hotspot

Settings → Network & Internet → Hotspot & Tethering → Wi-Fi Hotspot → On.
Note the hotspot's Wi-Fi name and password.

### 2. Start the server

In Termux:

```bash
cd bill-splitter
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Find your phone's hotspot IP

In a second Termux session (swipe from the left edge → "New session"):

```bash
ip -4 addr show wlan0 | grep inet
```

The address is usually `192.168.43.1` or `192.168.49.1`, but confirm it —
it varies by device.

### 4. Share the link

- Guests join your hotspot Wi-Fi network
- Open `http://<your-ip>:8000` on the host phone, upload the bill photo,
  create the session
- Share the join link, or let guests scan the QR code the app generates —
  it already points at whatever address they're connecting through, no
  configuration needed

### 5. Shut down afterward

Once the bill is settled: `Ctrl+C` in Termux to stop the server, then turn
the hotspot back off. Sessions are in-memory only, so nothing lingers after
you stop the process.

---

## Keeping Termux Alive

Android will suspend or kill background processes to save battery, which
would drop guests mid-session. For the few minutes you need it:

- Keep the Termux app in the foreground (don't switch away from it), or
- Pull down the Termux notification and tap **"Acquire wakelock"** to stop
  Android from suspending it while your screen is off
- Turn off battery optimization for Termux: Settings → Apps → Termux →
  Battery → Unrestricted

---

## Troubleshooting

**Guests can't reach the page** — Confirm they're actually connected to
your hotspot (not their own mobile data), and that you're using the IP from
`ip -4 addr show wlan0`, not `localhost`.

**Pillow install fails** — Use `pkg install python-pillow` instead of pip
(see step 4 above).

**Server stops when you switch apps** — Acquire the wakelock from the
Termux notification, or keep Termux in the foreground for the duration.

**Hotspot has no guests joining** — Some Android versions cap hotspot
clients around 5–10 devices; check Settings → Hotspot for a connected-device
limit if a guest can't join.
