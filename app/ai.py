from functools import lru_cache

from .config import get_settings
from .schemas import NutritionTip, PlanUpdate, UserInput, WorkoutPlan

settings = get_settings()

@lru_cache
def get_client():
    from google import genai
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to your .env file before generating a plan."
        )
    return genai.Client(api_key=settings.gemini_api_key)

def _generate(model: str, prompt: str, schema: type):
    client = get_client()
    from google.genai import types
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return schema.model_validate_json(response.text)

def generate_workout(user: UserInput) -> WorkoutPlan:
    prompt = f"""
You are FitBuddy, a cautious wellness-planning assistant for adults.
Create a practical 7-day general fitness plan.

User:
- age: {user.age}
- weight: {user.weight} kg
- goal: {user.goal}
- preferred intensity: {user.intensity}

Rules:
- Do not diagnose, prescribe treatment, or claim medical outcomes.
- Do not recommend extreme dieting, starvation, dehydration, unsafe exercise, or rapid weight loss.
- Keep intensity appropriate to the requested level.
- Include rest/recovery where appropriate.
- Use common exercises that can be done with little or no equipment.
- For every day provide warm-up, exercises with sets/reps or duration, rest, and cooldown.
- If an exercise could be unsuitable for someone with an injury or medical condition, tell the user to consult a qualified professional.
- Return exactly 7 days.
"""
    return _generate(settings.workout_model, prompt, WorkoutPlan)

def generate_nutrition_tip(user: UserInput) -> NutritionTip:
    prompt = f"""
Give one concise, practical nutrition/recovery tip for an adult whose goal is {user.goal}.
Avoid calorie targets, restrictive dieting, supplements, medical claims, or promises.
Emphasize balanced meals, hydration, adequate food intake, sleep, and recovery when relevant.
Return only the requested JSON structure.
"""
    return _generate(settings.tip_model, prompt, NutritionTip)

def update_workout_plan(user: UserInput, original_plan: str, feedback: str) -> PlanUpdate:
    prompt = f"""
Update this adult user's existing 7-day wellness workout plan using their feedback.

User goal: {user.goal}
Intensity preference: {user.intensity}
Feedback: {feedback}

Existing plan:
{original_plan}

Rules:
- Preserve useful structure while applying the feedback.
- Do not diagnose or provide medical treatment.
- Do not introduce extreme training, starvation, dehydration, or unsafe challenges.
- Include recovery/rest.
- Return exactly 7 days.
"""
    return _generate(settings.workout_model, prompt, PlanUpdate)
