from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from starlette.templating import Jinja2Templates
import os
import io
import uuid
from datetime import datetime
import qrcode

from ..store import create_session, get_session, update_session
from ..models import Session, Participant, BillItem
from ..bill_parser import parse_bill_image
from ..calculations import compute_totals

templates_dir = os.path.join(os.path.dirname(__file__), "../templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()


@router.post("/sessions")
def create_new_session(
    request: Request,
    file: UploadFile = File(...),
    host_name: str = Form(...),
):
    """Upload bill image and create a new session."""
    try:
        raw_bytes = file.file.read()

        # Parse the bill
        parsed_bill = parse_bill_image(raw_bytes)

        # Create session and host participant
        session_id = uuid.uuid4().hex[:12]
        host = Participant(name=host_name)

        items = [
            BillItem(
                name=item.name,
                unit_price=item.unit_price,
                quantity=item.quantity,
            )
            for item in parsed_bill.items
        ]

        session = Session(
            id=session_id,
            created_at=datetime.now(),
            host_id=host.id,
            participants={host.id: host},
            items=items,
            subtotal=parsed_bill.subtotal,
            tax=parsed_bill.tax,
            tip=parsed_bill.tip,
            total=parsed_bill.total,
        )

        create_session(session)

        # Redirect to session page with participant cookie
        response = RedirectResponse(url=f"/sessions/{session_id}", status_code=303)
        response.set_cookie(f"pid_{session_id}", host.id, httponly=True)
        return response

    except ValueError as e:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"error": str(e)},
            status_code=400,
        )


@router.post("/sessions/{session_id}/join")
def join_session(
    session_id: str,
    request: Request,
    participant_name: str = Form(...),
):
    """Join an existing session as a new participant."""
    session = get_session(session_id)
    if not session:
        return templates.TemplateResponse(request, "404.html", status_code=404)

    # Create new participant and add to session
    participant = Participant(name=participant_name)
    session.participants[participant.id] = participant
    session.version += 1
    update_session(session)

    # Redirect to session page with participant cookie
    response = RedirectResponse(url=f"/sessions/{session_id}", status_code=303)
    response.set_cookie(f"pid_{session_id}", participant.id, httponly=True)
    return response


@router.post("/sessions/{session_id}/items/{item_id}/claim")
def claim_unit(session_id: str, item_id: str, request: Request, action: str = "add"):
    """Claim or unclaim a single unit of an item."""
    session = get_session(session_id)
    if not session:
        return Response(status_code=404)

    participant_id = request.cookies.get(f"pid_{session_id}")
    if not participant_id or participant_id not in session.participants:
        return Response(status_code=403)

    # Find the item and update the claim quantity
    for item in session.items:
        if item.id == item_id:
            current_qty = item.claimed_by.get(participant_id, 0)

            if action == "add":
                # Claim one more unit (don't exceed available quantity)
                if current_qty < item.quantity:
                    item.claimed_by[participant_id] = current_qty + 1
            elif action == "remove":
                # Unclaim one unit
                if current_qty > 0:
                    new_qty = current_qty - 1
                    if new_qty == 0:
                        del item.claimed_by[participant_id]
                    else:
                        item.claimed_by[participant_id] = new_qty
            break

    session.version += 1
    update_session(session)

    return Response(status_code=204)


@router.get("/sessions/{session_id}/fragment")
def get_fragment(session_id: str, request: Request):
    """Return the live item list + totals for polling."""
    session = get_session(session_id)
    if not session:
        return Response("Not found", status_code=404)

    participant_id = request.cookies.get(f"pid_{session_id}")
    if not participant_id or participant_id not in session.participants:
        return Response("Forbidden", status_code=403)

    participant = session.participants[participant_id]
    totals = compute_totals(session)
    my_total = next((t for t in totals if t.participant_id == participant_id), None)

    # Calculate unclaimed totals
    unclaimed_items = [item for item in session.items if not item.claimed_by]
    unclaimed_count = len(unclaimed_items)
    unclaimed_items_total = sum(item.total_price for item in unclaimed_items)

    return templates.TemplateResponse(request, "_fragment.html", {
        "session_id": session_id,
        "session": session,
        "participant_id": participant_id,
        "participant": participant,
        "my_total": my_total,
        "totals": totals,
        "unclaimed_count": unclaimed_count,
        "unclaimed_items_total": unclaimed_items_total,
    })


@router.get("/sessions/{session_id}/qr.png")
def get_qr_code(session_id: str, request: Request):
    """Generate a QR code for the join URL."""
    session = get_session(session_id)
    if not session:
        return Response("Not found", status_code=404)

    # Build the absolute join URL
    base_url = f"{request.url.scheme}://{request.headers.get('host')}"
    join_url = f"{base_url}/sessions/{session_id}/join"

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(join_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Return as PNG
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")
