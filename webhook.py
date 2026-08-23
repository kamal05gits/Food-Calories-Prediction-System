from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
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


def send_outgoing_webhook(target_url: str, payload_data: Dict[str, Any]) -> bool:
    try:
        response = requests.post(target_url, json=payload_data, timeout=10)
        return response.status_code in (200, 201, 202, 204)
    except Exception as e:
        print(f"Failed to dispatch outgoing webhook: {e}")
        return False


webhook_app = FastAPI(
    title="Smart Food Calorie Webhook Integration API",
    version="1.0.0",
    description="Dedicated webhook listener and dispatcher for n8n, Zapier, Make, and automated workflows."
)


@webhook_app.get("/health")
def webhook_health():
    return {
        "status": "ok" if model is not None else "error",
        "webhook_service": "active",
        "model_loaded": model is not None
    }


@webhook_app.post("/webhook")
@webhook_app.post("/webhook/predict")
async def handle_incoming_webhook(request: Request):
    if model is None:
        raise HTTPException(status_code=500, detail=f"ML Model not loaded: {MODEL_LOAD_ERROR}")

    try:
        raw_body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body in webhook request.")

    parsed = parse_webhook_payload(raw_body)

    df_feat = pd.DataFrame([[
        parsed["serving_weight"],
        parsed["protein"],
        parsed["carbohydrates"],
        parsed["total_fat"],
        parsed["dietary_fiber"]
    ]], columns=FEATURES)

    pred_calories = round(float(np.clip(model.predict(df_feat)[0], 0, 3000)), 2)
    category, risk_level = classify_food(pred_calories)
    rec = generate_recommendation(
        risk_level, parsed["serving_weight"], parsed["protein"],
        parsed["carbohydrates"], parsed["total_fat"], parsed["dietary_fiber"]
    )

    result_payload = {
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
        "predictions": {
            "predicted_calories_kcal": pred_calories,
            "calorie_category": category,
            "dietary_risk_level": risk_level,
            "actionable_recommendation": rec
        }
    }

    callback_url = raw_body.get("callback_url") or raw_body.get("webhook_url")
    if callback_url:
        dispatched = send_outgoing_webhook(callback_url, result_payload)
        result_payload["callback_dispatched"] = dispatched

    return result_payload


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(webhook_app, host="0.0.0.0", port=8001)
