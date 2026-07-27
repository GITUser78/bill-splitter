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

### 2. Clone the repo

```bash
pkg install git -y
git clone https://github.com/GITUser78/bill-splitter.git
cd bill-splitter
```

### 3. Run the setup script

```bash
./setup-termux.sh
```

This installs the system packages the app needs, including Termux's own
precompiled builds of a few dependencies that don't build from source on
Android (see Troubleshooting below for why), then installs the rest via
pip and creates `.env` from `.env.example` if it's missing.

<details>
<summary>Manual setup (if you'd rather not use the script)</summary>

```bash
pkg update
pkg install python git libjpeg-turbo python-cryptography tur-repo
pkg install python-pillow python-grpcio python-watchfiles
pip install -r requirements.txt
cp .env.example .env
```

`libjpeg-turbo` lets Pillow's image resizing work without a slow
from-source build. `python-cryptography`, `python-pillow`, `python-grpcio`,
and `python-watchfiles` are Termux's precompiled builds of packages that
`google-generativeai` and `uvicorn[standard]` pull in indirectly — pip's
versions either fail to build or fail to import on Termux's Python (see
Troubleshooting below), so install them via `pkg` *before* the `pip
install` step so pip sees they're already satisfied and leaves them alone.

</details>

### 4. Set your Gemini API key

Edit `.env` (created by `setup-termux.sh`) and paste your key:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 5. Test it once

```bash
./start-termux.sh
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
./start-termux.sh
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
(see step 3 above).

**`watchfiles`/`maturin` build failure** (`Target triple not supported by
rustup: aarch64-unknown-linux-android`) — `uvicorn[standard]` depends on
`watchfiles`, which is written in Rust; PyPI has no prebuilt wheel for
Android ARM64, so pip tries (and fails) to compile it from source. Fix:

```bash
pip uninstall watchfiles -y
pkg install tur-repo -y
pkg install python-watchfiles -y
```

**`grpcio` wheel build failure** (`failed-wheel-build-for-install`) —
`google-generativeai` pulls in `grpcio`, which needs a C++ toolchain built
against gRPC/OpenSSL that isn't set up by default in Termux. Fix the same
way, via Termux's precompiled build:

```bash
pip uninstall grpcio -y
pkg install tur-repo -y
pkg install python-grpcio -y
```

If you hit either of these on a fresh install, `setup-termux.sh` already
installs both `python-watchfiles` and `python-grpcio` via `tur-repo` before
running `pip install`, so pip never tries to build them itself.

**`ImportError: dlopen failed: cannot locate symbol "PyLong_Type"` mentioning
`cryptography/hazmat/bindings/_rust.abi3.so`** — pip installed a version of
`cryptography` (pulled in indirectly by `google-generativeai`) that's
incompatible with Termux's Python build. Fix it by swapping in Termux's own
precompiled package:

```bash
pip uninstall cryptography -y
pkg install python-cryptography
```

Then re-run `./start-termux.sh`. If you hit this on a fresh install,
`setup-termux.sh` already installs `python-cryptography` before running
`pip install`, so pip never installs its own broken copy.

**Server stops when you switch apps** — Acquire the wakelock from the
Termux notification, or keep Termux in the foreground for the duration.

**Hotspot has no guests joining** — Some Android versions cap hotspot
clients around 5–10 devices; check Settings → Hotspot for a connected-device
limit if a guest can't join.
