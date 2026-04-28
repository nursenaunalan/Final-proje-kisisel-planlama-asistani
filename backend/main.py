from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import PlanRequest, DailyPlan
from .agent import generate_daily_plan
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Agent Personal Planning API")

# Allow CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-plan", response_model=DailyPlan)
async def generate_plan_endpoint(request: PlanRequest):
    try:
        logging.info(f"Received request: {request.raw_text}")
        plan = generate_daily_plan(
            raw_text=request.raw_text,
            start_hour=request.start_hour,
            end_hour=request.end_hour
        )
        return plan
    except Exception as e:
        logging.error(f"Error generating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
