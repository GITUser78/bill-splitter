from fastapi import APIRouter, Request

from ..templating import templates

router = APIRouter()


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/sessions/{session_id}")
def session_page(session_id: str, request: Request):
    from ..store import get_session

    session = get_session(session_id)
    if not session:
        return templates.TemplateResponse(request, "404.html", status_code=404)

    # Check if the user has a participant cookie for this session
    participant_id = request.cookies.get(f"pid_{session_id}")
    if not participant_id or participant_id not in session.participants:
        return templates.TemplateResponse(request, "join.html", {"session_id": session_id})

    return templates.TemplateResponse(request, "session.html", {
        "session_id": session_id,
        "session": session,
        "participant_id": participant_id,
    })


@router.get("/sessions/{session_id}/join")
def join_page(session_id: str, request: Request):
    from ..store import get_session

    session = get_session(session_id)
    if not session:
        return templates.TemplateResponse(request, "404.html", status_code=404)

    return templates.TemplateResponse(request, "join.html", {"session_id": session_id})
