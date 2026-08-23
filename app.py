import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import joblib
import numpy as np
import pandas as pd
import requests

from fci import classify_food, generate_recommendation

from main import (
    MASTER_CSV_FILE,
    MASTER_XLSX_FILE,
    append_to_master_csv,
    append_to_master_xlsx
)


N8N_WEBHOOK_URL = (
    "https://kamal-005.app.n8n.cloud/webhook/food-calorie-agent"
)



MODEL_PATH = "calorie_model.pkl"

try:
    model = joblib.load(MODEL_PATH)

except Exception as exc:
    model = None
    print("Model loading error:", exc)



root = tk.Tk()

root.title(
    "Food Calorie Prediction System"
)

root.geometry(
    "750x850"
)

root.configure(
    bg="#f4f6f9"
)




header = tk.Label(
    root,

    text="Food Calorie Predictor",

    font=(
        "Helvetica",
        18,
        "bold"
    ),

    bg="#b23a1d",

    fg="white",

    pady=12
)

header.pack(
    fill=tk.X
)



form_frame = tk.Frame(
    root,

    bg="#f4f6f9",

    padx=25,

    pady=15
)

form_frame.pack(
    fill=tk.BOTH,

    expand=True
)


fields = [

    (
        "Food Name:",
        "entry_name"
    ),

    (
        "Serving Size (g):",
        "entry_serving"
    ),

    (
        "Protein (g per 100 g):",
        "entry_protein"
    ),

    (
        "Carbohydrates (g per 100 g):",
        "entry_carbs"
    ),

    (
        "Total Fat (g per 100 g):",
        "entry_fat"
    ),

    (
        "Dietary Fiber (g per 100 g):",
        "entry_fiber"
    ),

    (
        "Sugars (g per 100 g):",
        "entry_sugar"
    ),
]


entries = {}


for idx, (
    label_text,
    key
) in enumerate(fields):

    lbl = tk.Label(

        form_frame,

        text=label_text,

        font=(
            "Helvetica",
            11
        ),

        bg="#f4f6f9",

        anchor="w"
    )

    lbl.grid(
        row=idx,

        column=0,

        sticky="w",

        pady=6
    )


    ent = tk.Entry(

        form_frame,

        font=(
            "Helvetica",
            11
        ),

        width=35
    )

    ent.grid(

        row=idx,

        column=1,

        pady=6,

        padx=10
    )


    entries[key] = ent



result_frame = tk.LabelFrame(

    root,

    text="Prediction Summary",

    font=(
        "Helvetica",
        12,
        "bold"
    ),

    bg="#ffffff",

    padx=15,

    pady=10
)

result_frame.pack(

    fill=tk.BOTH,

    padx=25,

    pady=10
)


lbl_res_cal = tk.Label(

    result_frame,

    text="Predicted Calories: --",

    font=(
        "Helvetica",
        11
    ),

    bg="#ffffff"
)

lbl_res_cal.pack(
    anchor="w",
    pady=2
)


lbl_res_class = tk.Label(

    result_frame,

    text="Calorie Class / Caution: --",

    font=(
        "Helvetica",
        11
    ),

    bg="#ffffff"
)

lbl_res_class.pack(
    anchor="w",
    pady=2
)


lbl_res_rec = tk.Label(

    result_frame,

    text="Recommendation: --",

    font=(
        "Helvetica",
        10,
        "italic"
    ),

    fg="#0d6efd",

    bg="#ffffff",

    wraplength=650,

    justify="left"
)

lbl_res_rec.pack(
    anchor="w",

    pady=4
)



lbl_agent = tk.Label(

    result_frame,

    text="n8n Agent: --",

    font=(
        "Helvetica",
        10,
        "bold"
    ),

    fg="#198754",

    bg="#ffffff",

    wraplength=650,

    justify="left"
)

lbl_agent.pack(

    anchor="w",

    pady=8
)



def log_prediction(record):

    """
    Save prediction to the existing
    CSV and XLSX files.
    """

    df = pd.DataFrame(
        [record]
    )

    append_to_master_csv(
        df
    )

    append_to_master_xlsx(
        df
    )



def send_to_n8n(record):

    """
    Send the prediction record to the
    n8n webhook.
    """

    payload = {

        "food_name":
            record["Food Name"],

        "serving_size":
            record["Serving Size (g)"],

        "protein":
            record["Protein (g)"],

        "carbohydrates":
            record["Carbohydrates (g)"],

        "total_fat":
            record["Total Fat (g)"],

        "dietary_fiber":
            record["Dietary Fiber (g)"],

        "sugars":
            record["Sugars (g)"],

        "predicted_calories":
            record["Predicted Calories (kcal)"],

        "calorie_class":
            record["Calorie Class"],

        "diet_caution_level":
            record["Diet Caution Level"],

        "recommendation":
            record["Dietary Recommendation"],

        "timestamp":
            record["Timestamp"]
    }


    print("\n================================")
    print("Sending data to n8n...")
    print("================================")

    print(payload)


    try:

        response = requests.post(

            N8N_WEBHOOK_URL,

            json=payload,

            timeout=30
        )


        response.raise_for_status()


        print(
            "n8n connection successful."
        )

        print(
            "HTTP Status:",
            response.status_code
        )

        print(
            "n8n Response:",
            response.text
        )



        try:

            return response.json()

        except ValueError:

            return {
                "status": "success",
                "response": response.text
            }


    except requests.exceptions.Timeout:

        print(
            "ERROR: n8n request timed out."
        )

        return {
            "status": "error",
            "message": "n8n request timed out."
        }


    except requests.exceptions.ConnectionError:

        print(
            "ERROR: Could not connect to n8n."
        )

        return {
            "status": "error",
            "message": "Could not connect to n8n."
        }


    except requests.exceptions.HTTPError as exc:

        print(
            "ERROR: n8n HTTP error:",
            exc
        )

        return {
            "status": "error",
            "message": str(exc)
        }


    except requests.exceptions.RequestException as exc:

        print(
            "ERROR: n8n request failed:",
            exc
        )

        return {
            "status": "error",
            "message": str(exc)
        }



def run_prediction():

    try:

       
        serving = float(
            entries[
                "entry_serving"
            ].get().strip()
        )

        protein = float(
            entries[
                "entry_protein"
            ].get().strip()
        )

        carbs = float(
            entries[
                "entry_carbs"
            ].get().strip()
        )

        fat = float(
            entries[
                "entry_fat"
            ].get().strip()
        )

        fiber = float(
            entries[
                "entry_fiber"
            ].get().strip()
        )

        sugar = float(
            entries[
                "entry_sugar"
            ].get().strip()
        )


       
        if serving <= 0:

            raise ValueError(
                "Serving size must be greater than 0."
            )

        if protein < 0:

            raise ValueError(
                "Protein cannot be negative."
            )

        if carbs < 0:

            raise ValueError(
                "Carbohydrates cannot be negative."
            )

        if fat < 0:

            raise ValueError(
                "Fat cannot be negative."
            )

        if fiber < 0:

            raise ValueError(
                "Fiber cannot be negative."
            )

        if sugar < 0:

            raise ValueError(
                "Sugar cannot be negative."
            )


      
        if model is not None:

            features = np.array(
                [[
                    serving,
                    protein,
                    carbs,
                    fat,
                    fiber,
                    sugar
                ]],

                dtype=float
            )


            calories = float(
                model.predict(
                    features
                )[0]
            )


        else:

            # Fallback calculation

            calories = (

                protein * 4

                + carbs * 4

                + fat * 9

                + fiber * 2

            ) * serving / 100.0


    
        calories = round(

            float(
                np.clip(
                    calories,
                    0,
                    2000
                )
            ),

            2
        )



        calorie_class, caution = (
            classify_food(
                calories
            )
        )


        rec = generate_recommendation(

            caution,

            serving,

            protein,

            carbs,

            fat,

            fiber,

            sugar
        )


       
        lbl_res_cal.config(

            text=(
                "Predicted Calories: "
                f"{calories:.2f} kcal"
            )
        )


        lbl_res_class.config(

            text=(
                "Calorie Class: "
                f"{calorie_class}  |  "
                f"Caution Level: {caution}"
            )
        )


        lbl_res_rec.config(

            text=(
                "Recommendation: "
                f"{rec}"
            )
        )

        food_name = (
            entries[
                "entry_name"
            ].get().strip()
            or
            "Unnamed Food"
        )

        record = {

            "Food Name":
                food_name,

            "Serving Size (g)":
                serving,

            "Protein (g)":
                protein,

            "Carbohydrates (g)":
                carbs,

            "Total Fat (g)":
                fat,

            "Dietary Fiber (g)":
                fiber,

            "Sugars (g)":
                sugar,

            "Predicted Calories (kcal)":
                calories,

            "Calorie Class":
                calorie_class,

            "Diet Caution Level":
                caution,

            "Dietary Recommendation":
                rec,

            "Timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
        }

        try:

            log_prediction(
                record
            )


            lbl_status.config(

                text=(
                    f"Saved '{food_name}' to "
                    f"{os.path.basename(MASTER_CSV_FILE)} "
                    f"and "
                    f"{os.path.basename(MASTER_XLSX_FILE)}"
                ),

                fg="#008272"
            )


        except Exception as exc:

            lbl_status.config(

                text=(
                    "Prediction shown, "
                    "but saving failed: "
                    f"{exc}"
                ),

                fg="#d9534f"
            )

        lbl_agent.config(
            text="n8n Agent: Sending prediction..."
        )

        root.update_idletasks()


        n8n_result = send_to_n8n(
            record
        )


        if n8n_result:

            if (
                n8n_result.get(
                    "status"
                )
                == "error"
            ):

                message = (
                    n8n_result.get(
                        "message",
                        "Unknown n8n error"
                    )
                )


                lbl_agent.config(

                    text=(
                        "n8n Agent Error: "
                        f"{message}"
                    ),

                    fg="#d9534f"
                )


            else:

                agent_response = (

                    n8n_result.get(
                        "agent_response"
                    )

                    or

                    n8n_result.get(
                        "output"
                    )

                    or

                    n8n_result.get(
                        "recommendation"
                    )

                    or

                    n8n_result.get(
                        "response"
                    )

                    or

                    str(
                        n8n_result
                    )
                )


                lbl_agent.config(

                    text=(
                        "n8n Agent:\n"
                        f"{agent_response}"
                    ),

                    fg="#198754"
                )


        else:

            lbl_agent.config(

                text=(
                    "n8n Agent: "
                    "No response received."
                ),

                fg="#d9534f"
            )


    except ValueError as exc:

        messagebox.showerror(

            "Invalid Input",

            str(exc)
        )


    except Exception as exc:

        messagebox.showerror(

            "Prediction Error",

            f"An unexpected error occurred:\n\n{exc}"
        )



btn_predict = tk.Button(

    root,

    text="Predict Calories",

    font=(
        "Helvetica",
        12,
        "bold"
    ),

    bg="#b23a1d",

    fg="white",

    padx=15,

    pady=8,

    command=run_prediction
)

btn_predict.pack(
    pady=10
)



lbl_status = tk.Label(

    root,

    text=(
        "Every prediction is stored in "
        "food_prediction.csv and "
        "food_prediction.xlsx"
    ),

    font=(
        "Helvetica",
        9
    ),

    fg="#555555",

    bg="#f4f6f9"
)

lbl_status.pack(
    pady=(0, 10)
)


if __name__ == "__main__":

    root.mainloop()
