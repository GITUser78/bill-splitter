# Bill Splitter

A web app for splitting restaurant bills among multiple diners. One person photographs the bill, and others join to select which items they consumed.

## Features

- 📸 Upload a bill photo — Claude vision API extracts items, prices, tax, and tip
- 👥 Multiple participants join via shareable link or QR code
- ✅ Claim items you consumed — whole-item claiming with even splits
- 💰 Real-time totals — each person sees how much they owe
- 📱 Mobile-friendly — responsive web interface, works over LAN HTTP

## Setup

### Prerequisites

- Python 3.13+
- `ANTHROPIC_API_KEY` environment variable or `.env` file

### Installation

```bash
# Clone or navigate to the project directory
cd /home/sta/Dokumente/Coding/python/Hello

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, ANTHROPIC_API_KEY from environment also works)
cp .env.example .env
# Edit .env and add your API key
```

### Running

**Important:** Must run as a single process (no workers). The app uses in-memory session storage with threading locks.

```bash
# Start the server on 0.0.0.0:8000 (accessible from your LAN)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Then open http://<your-lan-ip>:8000 on a phone or browser
```

## How It Works

1. **Host** uploads a bill photo
   - Claude vision API extracts items, prices, tax/tip using structured outputs
   - A session is created with all items available to claim

2. **Guests** join via link or QR code
   - Enter their name and join the session
   - See the same item list in real-time

3. **Everyone** claims their items
   - Tap an item to claim it
   - If multiple people claim an item, it's split evenly
   - Polling (2-second intervals) keeps totals up-to-date

4. **Final totals** show:
   - Each person's claimed subtotal
   - Proportional share of tax and tip (based on claimed items)
   - Total owed (subtotal + tax + tip)

## Architecture

### Backend

- **FastAPI** — web framework
- **Jinja2** — server-side template rendering
- **Claude vision API** (structured outputs) — bill parsing
- **In-memory store** with `threading.Lock` — session management
- **Polling** (2-second intervals) — live updates (not WebSockets)

### Frontend

- **Vanilla JavaScript** — fetch + DOM updates
- **Responsive CSS** — works on phone and desktop
- **No build step** — plain HTML/CSS/JS

### Data Model

- **Session** — id, host, participants, items, totals, version
- **Participant** — id, name
- **BillItem** — name, unit_price, quantity, claimed_by (set of participant IDs)
- **Decimal arithmetic** — money calculations are precise

### Calculation Logic

1. For each item with claims: `share = item.total_price / num_claimers`
2. Each participant's claimed subtotal = sum of their claimed item shares
3. Tax/tip split proportionally based on claimed subtotal ratio (handles unclaimed items)
4. Final total = claimed_subtotal + tax_share + tip_share

## Testing

### Worked Example

The regression test in `tests/test_calculations.py` verifies the split math:

```
Bill: Burger ($10) + Fries ($5) + Coke ($3)
Subtotal: $18, Tax: $1.80, Tip: $3.60, Total: $23.40

A claims Burger + Coke ($13) → owes $16.90
B claims Fries ($5) → owes $6.50
Sum: $23.40 ✓
```

Run the test (requires pytest and dependencies):

```bash
pytest tests/test_calculations.py -v
```

### Manual E2E Test

1. Open http://localhost:8000/ on your phone or desktop
2. Upload a bill photo (or use a test image)
3. Share the link or scan the QR code on another device
4. Both devices join and claim different items
5. Verify totals update within 2–3 seconds
6. Restart the server — all sessions clear (in-memory only)

## Limitations & Future Work

### Current

- **Single-process only** — no multi-worker deployment (uses in-memory store)
- **Whole-item claiming** — can't split a single item (e.g., 1 of 3 fries)
- **No persistence** — sessions lost on restart
- **LAN only** — designed for local use (HTTP works over LAN, not public internet)
- **Basic error handling** — bill parsing errors are user-facing messages

### Future Enhancements

- Per-unit item claiming (split 3 fries individually)
- Database persistence
- User accounts and history
- Receipt image storage
- Tip adjustment UI
- Venmo/PayPal integration
- Push notifications when totals change

## Configuration

Edit `app/config.py`:

```python
MODEL = "claude-opus-4-8"  # Change Claude model
MAX_IMAGE_DIMENSION = 1568  # Max image size for vision
POLL_INTERVAL_MS = 2000     # Live update frequency
```

## Troubleshooting

**Bill parsing fails:** The receipt photo is blurry or rotated. Try a clearer, straight-on photo.

**Session not found:** Sessions are in-memory only — restart the server clears them.

**Slow updates:** Polling is 2 seconds by default. Check `POLL_INTERVAL_MS` in `app/config.py`.

**CORS errors:** Not applicable — server renders all HTML/templates, no API-only requests.

## License

No license specified. This is a personal project.
