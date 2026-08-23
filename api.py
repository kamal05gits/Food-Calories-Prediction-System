from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fci import classify_food, generate_recommendation

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "calorie_model.pkl"

FEATURES = [
    "Serving Size (g)",
    "Protein (g)",
    "Carbohydrates (g)",
    "Total Fat (g)",
    "Dietary Fiber (g)",
    "Sugars (g)",
]

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:                       
    model = None
    MODEL_LOAD_ERROR = str(exc)
else:
    MODEL_LOAD_ERROR = None


class FoodInput(BaseModel):
    food_name: Optional[str] = None
    serving_size: float = Field(..., gt=0, le=1000)
    protein: float = Field(..., ge=0, le=100)
    carbohydrates: float = Field(..., ge=0, le=100)
    total_fat: float = Field(..., ge=0, le=100)
    dietary_fiber: float = Field(..., ge=0, le=40)
    sugars: float = Field(..., ge=0, le=100)


class PredictionResponse(BaseModel):
    food_name: Optional[str]
    predicted_calories: float
    calorie_class: str
    diet_caution_level: str
    recommendation: str


app = FastAPI(
    title="Food Calorie Prediction API",
    version="1.0.0",
    description="Prediction API for the Food Calorie Prediction n8n Agent.",
)


@app.get("/health")
def health():
    return {
        "status": "ok" if model is not None else "error",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH),
        "error": MODEL_LOAD_ERROR,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(food: FoodInput):
    if model is None:
        raise HTTPException(
            status_code=500,
            detail=f"Model could not be loaded: {MODEL_LOAD_ERROR}",
        )

    values = np.array([[
        food.serving_size,
        food.protein,
        food.carbohydrates,
        food.total_fat,
        food.dietary_fiber,
        food.sugars,
    ]], dtype=float)

    try:
        predicted = float(model.predict(values)[0])
    except Exception as exc:                     
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    predicted = round(float(np.clip(predicted, 0, 2000)), 2)
    calorie_class, caution_level = classify_food(predicted)

    recommendation = generate_recommendation(
        caution_level=caution_level,
        serving_size=food.serving_size,
        protein=food.protein,
        carbs=food.carbohydrates,
        fat=food.total_fat,
        fiber=food.dietary_fiber,
        sugar=food.sugars,
    )

    return PredictionResponse(
        food_name=food.food_name,
        predicted_calories=predicted,
        calorie_class=calorie_class,
        diet_caution_level=caution_level,
        recommendation=recommendation,
    )


@app.get("/")
def root():
    return {
        "service": "Food Calorie Prediction API",
        "endpoints": ["/health", "/predict"],
    }
