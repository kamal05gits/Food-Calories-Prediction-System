import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import joblib
import numpy as np
import pandas as pd

from fci import classify_food, generate_recommendation
from main import (MASTER_CSV_FILE, MASTER_XLSX_FILE,
                  append_to_master_csv, append_to_master_xlsx)

MODEL_PATH = "calorie_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None

root = tk.Tk()
root.title("Food Calorie Prediction System")
root.geometry("750x760")
root.configure(bg="#f4f6f9")

# Header
header = tk.Label(root, text="Food Calorie Predictor",
                  font=("Helvetica", 18, "bold"),
                  bg="#b23a1d", fg="white", pady=12)
header.pack(fill=tk.X)

form_frame = tk.Frame(root, bg="#f4f6f9", padx=25, pady=15)
form_frame.pack(fill=tk.BOTH, expand=True)

fields = [
    ("Food Name:", "entry_name"),
    ("Serving Size (g):", "entry_serving"),
    ("Protein (g per 100 g):", "entry_protein"),
    ("Carbohydrates (g per 100 g):", "entry_carbs"),
    ("Total Fat (g per 100 g):", "entry_fat"),
    ("Dietary Fiber (g per 100 g):", "entry_fiber"),
    ("Sugars (g per 100 g):", "entry_sugar"),
]

entries = {}
for idx, (label_text, key) in enumerate(fields):
    lbl = tk.Label(form_frame, text=label_text, font=("Helvetica", 11),
                   bg="#f4f6f9", anchor="w")
    lbl.grid(row=idx, column=0, sticky="w", pady=6)
    ent = tk.Entry(form_frame, font=("Helvetica", 11), width=35)
    ent.grid(row=idx, column=1, pady=6, padx=10)
    entries[key] = ent

result_frame = tk.LabelFrame(root, text="Prediction Summary",
                             font=("Helvetica", 12, "bold"),
                             bg="#ffffff", padx=15, pady=10)
result_frame.pack(fill=tk.BOTH, padx=25, pady=10)

lbl_res_cal = tk.Label(result_frame, text="Predicted Calories: --",
                       font=("Helvetica", 11), bg="#ffffff")
lbl_res_cal.pack(anchor="w", pady=2)

lbl_res_class = tk.Label(result_frame, text="Calorie Class / Caution: --",
                         font=("Helvetica", 11), bg="#ffffff")
lbl_res_class.pack(anchor="w", pady=2)

lbl_res_rec = tk.Label(result_frame, text="Recommendation: --",
                       font=("Helvetica", 10, "italic"), fg="#0d6efd",
                       bg="#ffffff", wraplength=650, justify="left")
lbl_res_rec.pack(anchor="w", pady=4)


def log_prediction(record):
    """Append one prediction record to the master CSV log AND the
    separate XLSX workbook (same shared storage used by ``main.py``)."""
    df = pd.DataFrame([record])
    append_to_master_csv(df)
    append_to_master_xlsx(df)


def run_prediction():
    try:
        serving = float(entries["entry_serving"].get().strip())
        protein = float(entries["entry_protein"].get().strip())
        carbs = float(entries["entry_carbs"].get().strip())
        fat = float(entries["entry_fat"].get().strip())
        fiber = float(entries["entry_fiber"].get().strip())
        sugar = float(entries["entry_sugar"].get().strip())

        if model:
            features = np.array([[serving, protein, carbs, fat, fiber, sugar]])
            calories = float(model.predict(features)[0])
        else:
            calories = (protein * 4 + carbs * 4 + fat * 9 + fiber * 2) \
                * serving / 100.0

        calories = round(calories, 2)
        calorie_class, caution = classify_food(calories)
        rec = generate_recommendation(caution, serving, protein, carbs,
                                      fat, fiber, sugar)

        lbl_res_cal.config(text=f"Predicted Calories: {calories:.2f} kcal")
        lbl_res_class.config(
            text=f"Calorie Class: {calorie_class}  |  Caution Level: {caution}")
        lbl_res_rec.config(text=f"Recommendation: {rec}")

        food_name = entries["entry_name"].get().strip() or "Unnamed Food"

        record = {
            "Food Name": food_name,
            "Serving Size (g)": serving,
            "Protein (g)": protein,
            "Carbohydrates (g)": carbs,
            "Total Fat (g)": fat,
            "Dietary Fiber (g)": fiber,
            "Sugars (g)": sugar,
            "Predicted Calories (kcal)": calories,
            "Calorie Class": calorie_class,
            "Diet Caution Level": caution,
            "Dietary Recommendation": rec,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
            log_prediction(record)
            lbl_status.config(
                text=f"Saved '{food_name}' to {os.path.basename(MASTER_CSV_FILE)}"
                     f" and {os.path.basename(MASTER_XLSX_FILE)}",
                fg="#008272")
        except Exception as exc:
            lbl_status.config(
                text=f"Prediction shown, but saving the log failed: {exc}",
                fg="#d9534f")

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please ensure all nutritional fields contain valid numeric inputs.")


btn_predict = tk.Button(root, text="Predict Calories",
                        font=("Helvetica", 12, "bold"),
                        bg="#b23a1d", fg="white", padx=15, pady=8,
                        command=run_prediction)
btn_predict.pack(pady=10)

lbl_status = tk.Label(
    root,
    text="Every prediction is stored in food_prediction.csv and food_prediction.xlsx",
    font=("Helvetica", 9), fg="#555555", bg="#f4f6f9")
lbl_status.pack(pady=(0, 10))

if __name__ == "__main__":
    root.mainloop()
