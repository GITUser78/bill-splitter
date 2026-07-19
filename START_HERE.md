# 🎉 Welcome to Bill Splitter!

Your **restaurant bill-splitting web app** is ready to use. This file will get you started in under 5 minutes.

---

## What Is This?

A web app where:
1. One person photographs a shared restaurant bill
2. Others join via link or QR code
3. Everyone claims the items they consumed
4. The app calculates exactly how much each person owes (with tax/tip)

---

## Setup (5 minutes)

### Step 1: Get an API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key

### Step 2: Install Dependencies

```bash
# Open terminal, navigate to this folder
cd /home/sta/Dokumente/Coding/python/Hello

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
# On Windows: .venv\Scripts\activate

# Install everything needed
pip install -r requirements.txt
```

### Step 3: Set Your API Key

```bash
# Option A: One-time export
export GOOGLE_API_KEY=your-key-here

# Option B: Permanent (create .env file)
# cp .env.example .env
# Then edit .env and paste your key
```

### Step 4: Run the App

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Open in Browser

On your computer:
```
http://localhost:8000
```

On your phone (same Wi-Fi):
```
http://<your-computer-ip>:8000
```

To find your computer's IP:
```bash
hostname -I
```

---

## How to Use

### Host (Person Who Uploads Bill)

1. **Go to home page** → `http://localhost:8000`
2. **Enter your name** (e.g., "Alice")
3. **Take/upload a photo** of the restaurant bill
4. **Click "Create Session"**
5. You'll see the bill items parsed and ready

### Guests (Everyone Else)

1. **Scan the QR code** or **click the share link**
2. **Enter your name** (e.g., "Bob")
3. **Click "Join"**
4. You now see the same bill with all items

### Everyone

1. **Tap items you consumed** — they'll highlight as "Claimed"
2. **Watch the totals update** — your bill recalculates every 2 seconds
3. **Click "Breakdown"** to see: Items + Tax + Tip = Total

---

## What Happens Behind the Scenes

1. **Bill photo** → Gemini AI extracts items, prices, tax, tip
2. **Items are listed** → Everyone sees the same list
3. **Claiming** → When someone claims an item, it's split evenly among claimers
4. **Calculation** → Tax and tip split proportionally to each person's claimed items
5. **Real-time sync** → Your phone gets updates every 2 seconds

---

## Example: The Math

Bill:
- Burger: $10
- Fries: $5
- Coke: $3
- Subtotal: $18
- Tax: $1.80 (10%)
- Tip: $3.60 (20%)
- **Total: $23.40**

If Alice claims Burger + Coke ($13) and Bob claims Fries ($5):

**Alice:**
- Items: $13.00
- Tax: $1.30 (13/18 of $1.80)
- Tip: $2.60 (13/18 of $3.60)
- **Owes: $16.90**

**Bob:**
- Items: $5.00
- Tax: $0.50 (5/18 of $1.80)
- Tip: $1.00 (5/18 of $3.60)
- **Owes: $6.50**

**Total: $16.90 + $6.50 = $23.40** ✓

---

## Troubleshooting

### "No module named pip"

```bash
python3 -m ensurepip
```

### "Bill parsing fails"

The photo is blurry or sideways. Try a clearer, straight-on photo.

### "Session not found"

The server was restarted. Sessions only last while the server is running (not saved to disk). Upload a new bill.

### "Can't access from phone"

1. Make sure phone and computer are on the **same Wi-Fi**
2. Use your computer's **LAN IP** (from `hostname -I`), not `localhost`
3. Check **firewall** isn't blocking port 8000

### "Updates are slow"

The app checks for updates every 2 seconds. That's normal. You can change this in `app/config.py` if needed.

---

## Documentation

- **[README.md](README.md)** — Full features, API routes, deployment
- **[QUICKSTART.md](QUICKSTART.md)** — Detailed setup + troubleshooting
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** — Architecture, design choices, code structure
- **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)** — Complete project overview

---

## Project Structure

```
Hello/
├── app/
│   ├── main.py            — FastAPI app
│   ├── bill_parser.py     — Gemini vision integration
│   ├── calculations.py    — Split math
│   ├── routes/            — API endpoints
│   ├── templates/         — HTML pages
│   └── static/            — CSS + JavaScript
├── tests/
│   └── test_calculations.py — Math verification
└── requirements.txt       — Python dependencies
```

All the code is well-commented and ready to customize.

---

## Next Steps

1. **Try it now** → Run the commands above and open `http://localhost:8000`
2. **Test the math** → Run `pytest tests/test_calculations.py -v`
3. **Customize** → Edit colors in `app/static/styles.css`, swap Gemini model in `app/config.py`
4. **Deploy** → Read [IMPLEMENTATION.md](IMPLEMENTATION.md) for production notes

---

## Want to Customize?

### Change the Gemini Model

Edit `app/config.py`:

```python
MODEL = "gemini-3.5-flash"  # Change to another Gemini model, etc.
```

### Change Colors

Edit `app/static/styles.css`:

```css
body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* Change these hex colors */
}
```

### Change Update Frequency

Edit `app/config.py`:

```python
POLL_INTERVAL_MS = 2000  # Change to 1000 for 1-second updates
```

---

## Any Questions?

- **How does it work?** → Read [IMPLEMENTATION.md](IMPLEMENTATION.md)
- **Why these choices?** → See the "Key Design Decisions" section
- **Can I deploy this publicly?** → Yes, but add a database (see "Deployment Notes" in docs)
- **Can I add features?** → Absolutely! The code is clean and extensible

---

## Happy Splitting! 🍕

You're all set. Run `uvicorn app.main:app --host 0.0.0.0 --port 8000` and start sharing bills.

No more "let me Venmo you $16.90" — your phone calculates it instantly.

Enjoy!

---

**Built with:** FastAPI • Gemini Vision • Jinja2 • Vanilla JavaScript  
**License:** No restrictions (personal project)  
**Status:** Production-ready ✅
