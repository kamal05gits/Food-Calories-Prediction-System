from pathlib import Path
from typing import Optional, Dict, Any

import joblib
import numpy as np
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from fci import classify_food, generate_recommendation

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "calorie_model.pkl"

FEATURES = [
    "Serving Weight (g)",
    "Protein (g)",
    "Carbohydrates (g)",
    "Total Fat (g)",
    "Dietary Fiber (g)",
]

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    model = None
    MODEL_LOAD_ERROR = str(exc)
else:
    MODEL_LOAD_ERROR = None


class FoodInput(BaseModel):
    food_id: Optional[str] = None
    food_name: Optional[str] = None
    serving_weight: float = Field(..., ge=10, le=2000, description="Serving weight in grams")
    protein: float = Field(..., ge=0, le=200, description="Protein in grams")
    carbohydrates: float = Field(..., ge=0, le=300, description="Carbohydrates in grams")
    total_fat: float = Field(..., ge=0, le=200, description="Total fat in grams")
    dietary_fiber: float = Field(..., ge=0, le=100, description="Dietary fiber in grams")


class PredictionResponse(BaseModel):
    food_id: Optional[str]
    food_name: Optional[str]
    predicted_calories: float
    calorie_category: str
    dietary_risk_level: str
    recommendation: str


def parse_webhook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    food_id = str(payload.get("food_id") or payload.get("id") or "WEBHOOK_ITEM")
    food_name = str(payload.get("food_name") or payload.get("name") or payload.get("item") or "Webhook Food Item")

    serving_weight = float(payload.get("serving_weight") or payload.get("weight") or payload.get("serving") or 100.0)
    protein = float(payload.get("protein") or payload.get("prot") or 0.0)
    carbs = float(payload.get("carbohydrates") or payload.get("carbs") or payload.get("carb") or 0.0)
    fat = float(payload.get("total_fat") or payload.get("fat") or payload.get("fats") or 0.0)
    fiber = float(payload.get("dietary_fiber") or payload.get("fiber") or 0.0)

    return {
        "food_id": food_id,
        "food_name": food_name,
        "serving_weight": serving_weight,
        "protein": protein,
        "carbohydrates": carbs,
        "total_fat": fat,
        "dietary_fiber": fiber
    }


app = FastAPI(
    title="Smart Food Calorie Prediction & Webhook API",
    version="1.0.0",
    description="Prediction API, Webhook integration endpoint, and Web UI for n8n, Zapier, Make, and automated workflows.",
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

    values = pd.DataFrame([[
        food.serving_weight,
        food.protein,
        food.carbohydrates,
        food.total_fat,
        food.dietary_fiber,
    ]], columns=FEATURES)

    try:
        predicted = float(model.predict(values)[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    predicted = round(float(np.clip(predicted, 0, 3000)), 2)
    category, risk_level = classify_food(predicted)

    recommendation = generate_recommendation(
        risk_level=risk_level,
        serving_weight=food.serving_weight,
        protein=food.protein,
        carbs=food.carbohydrates,
        fat=food.total_fat,
        fiber=food.dietary_fiber,
    )

    return PredictionResponse(
        food_id=food.food_id,
        food_name=food.food_name,
        predicted_calories=predicted,
        calorie_category=category,
        dietary_risk_level=risk_level,
        recommendation=recommendation,
    )


@app.post("/webhook")
@app.post("/webhook/predict")
@app.post("/n8n/predict")
async def handle_webhook(request: Request):
    if model is None:
        raise HTTPException(status_code=500, detail=f"Model not loaded: {MODEL_LOAD_ERROR}")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or missing JSON payload in webhook request.")

    parsed = parse_webhook_payload(payload)

    values = pd.DataFrame([[
        parsed["serving_weight"],
        parsed["protein"],
        parsed["carbohydrates"],
        parsed["total_fat"],
        parsed["dietary_fiber"]
    ]], columns=FEATURES)

    predicted = round(float(np.clip(model.predict(values)[0], 0, 3000)), 2)
    category, risk_level = classify_food(predicted)

    recommendation = generate_recommendation(
        risk_level=risk_level,
        serving_weight=parsed["serving_weight"],
        protein=parsed["protein"],
        carbs=parsed["carbohydrates"],
        fat=parsed["total_fat"],
        fiber=parsed["dietary_fiber"],
    )

    response_data = {
        "event": "food_calorie_prediction",
        "status": "success",
        "food_id": parsed["food_id"],
        "food_name": parsed["food_name"],
        "nutritional_inputs": {
            "serving_weight_g": parsed["serving_weight"],
            "protein_g": parsed["protein"],
            "carbohydrates_g": parsed["carbohydrates"],
            "total_fat_g": parsed["total_fat"],
            "dietary_fiber_g": parsed["dietary_fiber"]
        },
        "prediction_results": {
            "predicted_calories_kcal": predicted,
            "calorie_category": category,
            "dietary_risk_level": risk_level,
            "actionable_recommendation": recommendation
        }
    }

    callback_url = payload.get("callback_url") or payload.get("webhook_url")
    if callback_url:
        try:
            resp = requests.post(callback_url, json=response_data, timeout=5)
            response_data["callback_status"] = "dispatched" if resp.status_code in (200, 201, 202, 204) else "failed"
        except Exception as err:
            response_data["callback_status"] = f"error: {str(err)}"

    return response_data


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Food Calorie Prediction System</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; color: #1e293b; margin: 0; padding: 20px; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
            h1 { color: #1e3a8a; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; font-size: 24px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
            label { font-weight: 600; font-size: 14px; color: #334155; }
            input { width: 100%; padding: 10px; margin-top: 4px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
            button { background-color: #1e3a8a; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 100%; margin-top: 20px; font-weight: bold; }
            button:hover { background-color: #1d4ed8; }
            .result-card { margin-top: 25px; padding: 20px; background-color: #f8fafc; border-left: 5px solid #3b82f6; border-radius: 6px; display: none; }
            .badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; color: white; background: #3b82f6; }
            .endpoint-info { margin-top: 30px; font-size: 13px; color: #64748b; background: #f1f5f9; padding: 15px; border-radius: 6px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 Smart Food Calorie Prediction System</h1>
            <p>Predict total food calories (kcal), classify energy level, and receive tailored dietary recommendations based on food macronutrients.</p>
            
            <form id="predForm">
                <div class="grid">
                    <div>
                        <label>Food ID:</label>
                        <input type="text" id="food_id" value="FOOD0101">
                    </div>
                    <div>
                        <label>Food Name:</label>
                        <input type="text" id="food_name" value="Grilled Chicken & Avocado Bowl">
                    </div>
                    <div>
                        <label>Serving Weight (g):</label>
                        <input type="number" id="serving_weight" value="350" step="0.1">
                    </div>
                    <div>
                        <label>Protein (g):</label>
                        <input type="number" id="protein" value="38" step="0.1">
                    </div>
                    <div>
                        <label>Carbohydrates (g):</label>
                        <input type="number" id="carbohydrates" value="25" step="0.1">
                    </div>
                    <div>
                        <label>Total Fat (g):</label>
                        <input type="number" id="total_fat" value="14" step="0.1">
                    </div>
                    <div style="grid-column: span 2;">
                        <label>Dietary Fiber (g):</label>
                        <input type="number" id="dietary_fiber" value="6" step="0.1">
                    </div>
                </div>
                <button type="submit">Predict Calorie Content</button>
            </form>

            <div id="resultCard" class="result-card">
                <h3 style="margin-top: 0; color: #1e3a8a;">Prediction Result</h3>
                <p><strong>Predicted Calories:</strong> <span id="resCal" style="font-size: 20px; font-weight: bold; color: #0f172a;">--</span></p>
                <p><strong>Calorie Category:</strong> <span id="resCat" class="badge">--</span> | <strong>Risk Level:</strong> <span id="resRisk">--</span></p>
                <p><strong>Dietary Recommendation:</strong> <span id="resRec" style="font-style: italic; color: #2563eb;">--</span></p>
            </div>

            <div class="endpoint-info">
                <strong>API & Webhook Endpoints:</strong><br>
                <code>GET /health</code> | <code>POST /predict</code> | <code>POST /webhook</code> | <code>POST /webhook/predict</code> | <code>GET /docs</code>
            </div>
        </div>

        <script>
            document.getElementById('predForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const payload = {
                    food_id: document.getElementById('food_id').value,
                    food_name: document.getElementById('food_name').value,
                    serving_weight: parseFloat(document.getElementById('serving_weight').value),
                    protein: parseFloat(document.getElementById('protein').value),
                    carbohydrates: parseFloat(document.getElementById('carbohydrates').value),
                    total_fat: parseFloat(document.getElementById('total_fat').value),
                    dietary_fiber: parseFloat(document.getElementById('dietary_fiber').value)
                };

                try {
                    const res = await fetch('/predict', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    
                    if (res.ok) {
                        document.getElementById('resCal').innerText = data.predicted_calories + ' kcal';
                        document.getElementById('resCat').innerText = data.calorie_category;
                        document.getElementById('resRisk').innerText = data.dietary_risk_level;
                        document.getElementById('resRec').innerText = data.recommendation;
                        document.getElementById('resultCard').style.display = 'block';
                    } else {
                        alert('Error: ' + JSON.stringify(data.detail));
                    }
                } catch (err) {
                    alert('Request failed: ' + err);
                }
            });
        </script>
    </body>
    </html>
    """
