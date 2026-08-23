# Hosting Bill Splitter Publicly (Render)

Run the app once, on a real server, so any guest can join from their own
mobile data — no Termux, no shared hotspot, no phone left running as a
server for the evening. This is a one-time setup for the host; guests
just open a link.

If you'd rather keep everything local and offline instead, see
[TERMUX_SETUP.md](TERMUX_SETUP.md) — that's still a valid option, just a
different trade-off (no internet needed, but guests must be on the host's
Wi-Fi).

---

## One-Time Setup

### 1. Push the repo to GitHub

Render deploys from a GitHub repo. If this repo isn't already on GitHub,
push it there first.

### 2. Get a Gemini API key

If you don't already have one: [Google AI Studio](https://aistudio.google.com/apikey).

### 3. Create the Render service

Go to [render.com](https://dashboard.render.com) and sign up (no credit
card required for the free tier).

**Option A — Blueprint (recommended):** New → Blueprint → connect this
repo. Render reads [render.yaml](render.yaml) and provisions the service
for you.

**Option B — Manual:** New → Web Service → connect this repo → Render
detects the [Dockerfile](Dockerfile) and picks the Docker runtime
automatically → choose the **Free** plan.

Either way, when prompted, set the environment variable:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

(Environment tab if you set up manually — enter it as a **Secret**, not a
plain value.)

### 4. Deploy and verify

Render builds the Docker image and gives you a URL like
`https://bill-splitter-xxxx.onrender.com`. Once the deploy finishes:

1. Open the URL — confirm the home page loads.
2. Create a session with a test bill photo.
3. Check the QR code / share link shown on the session page starts with
   `https://` (not `http://`). If it doesn't, the proxy header setup in
   the [Dockerfile](Dockerfile) isn't taking effect — worth re-checking
   before sharing with real guests.

That's it — send the join link or QR code to guests. They open it on
their own phone, on their own mobile data.

---

## Limitations to Know About

**Sessions are lost on restart.** The app keeps all session state in
memory (see `app/store.py`) — nothing is written to disk. A redeploy, a
crash, or the free tier spinning down all wipe every active session.
Don't redeploy while a bill-splitting session is in progress; if you need
to push a change, do it between uses.

**Never scale past one instance, and never add `--workers`.** Because
session state lives in a single process's memory, a second instance or
worker would have its own empty, independent copy — guests could get
routed to the "wrong" one and see a blank or missing session. Render's
free plan only runs one instance by default, so this is safe as long as
you don't change that.

**Free tier cold starts.** Render's free Web Service spins down after
~15 minutes with no traffic and takes roughly 30–60 seconds to wake back
up on the next request. In practice this only affects the very first
person to open the link for the night — once a session is active, the
app is polled every couple of seconds by every participant's phone, which
keeps it awake for the rest of the evening.

If cold starts are annoying or you want the app always warm, Render's
paid **Starter** plan (a few dollars/month) removes the spin-down with no
code changes needed — just switch the plan in the Render dashboard.
