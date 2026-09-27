import secrets

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from .ai import generate_nutrition_tip, generate_workout, update_workout_plan
from .config import get_settings
from .database import get_all_users, get_latest_plan, get_user, save_plan, save_user, update_plan
from .schemas import FeedbackRequest, UserInput

router = APIRouter()
settings = get_settings()

def templates(request: Request):
    return request.app.state.templates

# Jinja2Templates is mounted in main.py, so attach it once lazily.
def render(request: Request, name: str, context: dict):
    from fastapi.templating import Jinja2Templates
    from pathlib import Path
    base = Path(__file__).resolve().parent.parent
    return Jinja2Templates(directory=base / "templates").TemplateResponse(
        request=request, name=name, context=context
    )

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render(request, "index.html", {"request": request, "error": None})

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_route(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        if get_user(data.user_id):
            raise ValueError("That User ID already exists. Choose another one.")

        plan = generate_workout(data)
        tip = generate_nutrition_tip(data)

        user = save_user(data.model_dump())
        saved_plan = save_plan(
            user.id,
            plan.model_dump_json(indent=2),
            tip.model_dump_json(indent=2),
        )

        return render(request, "result.html", {
            "request": request,
            "user": data,
            "plan": plan,
            "tip": tip,
            "plan_id": saved_plan.id,
            "updated_plan": None,
            "message": "Your 7-day plan was generated successfully.",
        })
    except Exception as exc:
        return render(request, "index.html", {
            "request": request,
            "error": str(exc),
        })

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    try:
        feedback_request = FeedbackRequest(user_id=user_id, feedback=feedback)
        user_record = get_user(user_id)
        stored_plan = get_latest_plan(user_id)

        if not user_record or not stored_plan:
            raise ValueError("User ID was not found.")

        user = UserInput(
            username=user_record.username,
            user_id=user_record.user_id,
            age=user_record.age,
            weight=user_record.weight,
            goal=user_record.goal,
            intensity=user_record.intensity,
        )
        original = stored_plan.original_plan
        updated = update_workout_plan(user, original, feedback_request.feedback)
        saved = update_plan(user_id, updated.model_dump_json(indent=2), feedback_request.feedback)

        return render(request, "result.html", {
            "request": request,
            "user": user,
            "plan": None,
            "tip": None,
            "plan_id": saved.id if saved else None,
            "updated_plan": updated,
            "message": "Your plan was updated using your feedback.",
        })
    except Exception as exc:
        return render(request, "feedback.html", {
            "request": request,
            "error": str(exc),
        })

@router.get("/feedback", response_class=HTMLResponse)
def feedback_page(request: Request):
    return render(request, "feedback.html", {"request": request, "error": None})

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, token: str | None = None):
    if not token or not secrets.compare_digest(token, settings.admin_token):
        raise HTTPException(status_code=401, detail="Valid admin token required.")
    users = get_all_users()
    return render(request, "all_users.html", {
        "request": request,
        "users": users,
        "admin_token": token,
    })
