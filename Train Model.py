import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "food_calorie_dataset_1000.csv")
MODEL_PATH = os.path.join(BASE_DIR, "calorie_model.pkl")

FEATURE_COLS = [
    "Serving Size (g)",
    "Protein (g)",
    "Carbohydrates (g)",
    "Total Fat (g)",
    "Dietary Fiber (g)",
    "Sugars (g)",
]
TARGET_COL = "Calories (kcal)"
REQUIRED_COLS = ["Food Name", "Category"] + FEATURE_COLS + [TARGET_COL]

# Nutrient ranges are per 100 g, serving size in grams.
CATEGORY_PROFILES = {
    "Vegetables":       {"protein": (0.5, 3.0),  "carbs": (2, 15),   "fat": (0.0, 1.0),  "fiber": (1.0, 5.0),  "sugar": (1, 8),    "serving": (100, 250)},
    "Fruits":           {"protein": (0.2, 2.0),  "carbs": (8, 25),   "fat": (0.0, 1.5),  "fiber": (1.0, 4.0),  "sugar": (7, 20),   "serving": (100, 200)},
    "Dairy":            {"protein": (2.0, 12.0), "carbs": (3, 15),   "fat": (0.5, 25.0), "fiber": (0.0, 0.5),  "sugar": (3, 14),   "serving": (100, 250)},
    "Grains & Cereals": {"protein": (6.0, 14.0), "carbs": (55, 80),  "fat": (1.0, 7.0),  "fiber": (2.0, 11.0), "sugar": (0, 12),   "serving": (40, 200)},
    "Meat & Poultry":   {"protein": (18.0, 30.0),"carbs": (0, 3),    "fat": (3.0, 25.0), "fiber": (0.0, 0.2),  "sugar": (0, 1),    "serving": (100, 250)},
    "Seafood":          {"protein": (15.0, 26.0),"carbs": (0, 2),    "fat": (0.5, 15.0), "fiber": (0.0, 0.1),  "sugar": (0, 0.5),  "serving": (100, 200)},
    "Legumes":          {"protein": (5.0, 10.0), "carbs": (15, 30),  "fat": (0.5, 3.0),  "fiber": (4.0, 9.0),  "sugar": (0.5, 3),  "serving": (100, 200)},
    "Nuts & Seeds":     {"protein": (15.0, 25.0),"carbs": (7, 28),   "fat": (44.0, 65.0),"fiber": (3.0, 11.0), "sugar": (2, 7),    "serving": (20, 40)},
    "Snacks":           {"protein": (4.0, 8.0),  "carbs": (45, 65),  "fat": (20.0, 40.0),"fiber": (1.0, 4.0),  "sugar": (5, 25),   "serving": (25, 60)},
    "Beverages":        {"protein": (0.0, 3.5),  "carbs": (0, 14),   "fat": (0.0, 2.0),  "fiber": (0.0, 1.0),  "sugar": (0, 13),   "serving": (200, 350)},
    "Desserts":         {"protein": (2.0, 6.0),  "carbs": (35, 60),  "fat": (10.0, 30.0),"fiber": (0.0, 3.0),  "sugar": (20, 45),  "serving": (50, 120)},
    "Fast Food":        {"protein": (8.0, 15.0), "carbs": (25, 40),  "fat": (10.0, 25.0),"fiber": (1.0, 3.0),  "sugar": (3, 10),   "serving": (100, 300)},
}

FOOD_NAMES = {
    "Vegetables": ["Spinach", "Broccoli", "Carrot", "Cauliflower", "Bell Pepper",
                   "Cucumber", "Tomato", "Green Beans", "Cabbage", "Zucchini"],
    "Fruits": ["Apple", "Banana", "Orange", "Mango", "Grapes",
               "Papaya", "Pineapple", "Watermelon", "Guava", "Pomegranate"],
    "Dairy": ["Whole Milk", "Skim Milk", "Paneer", "Curd", "Greek Yogurt",
              "Cheddar Cheese", "Butter", "Cream", "Buttermilk", "Mozzarella"],
    "Grains & Cereals": ["Brown Rice", "White Rice", "Oats", "Whole Wheat Bread",
                         "Quinoa", "Cornflakes", "Barley", "Ragi", "Pasta", "Upma"],
    "Meat & Poultry": ["Chicken Breast", "Grilled Chicken", "Mutton Curry Cut",
                       "Turkey Breast", "Chicken Thigh", "Lean Beef", "Pork Loin",
                       "Duck Meat", "Keema", "Tandoori Chicken"],
    "Seafood": ["Salmon", "Rohu Fish", "Prawns", "Tuna", "Sardine",
                "Mackerel", "Crab", "Pomfret", "Squid", "Tilapia"],
    "Legumes": ["Boiled Chickpeas", "Toor Dal", "Moong Dal", "Black Beans",
                "Kidney Beans", "Masoor Dal", "Green Peas", "Soya Chunks",
                "Chana Dal", "Sprouted Moong"],
    "Nuts & Seeds": ["Almonds", "Cashews", "Walnuts", "Peanuts", "Pistachios",
                     "Sunflower Seeds", "Chia Seeds", "Pumpkin Seeds", "Flax Seeds", "Hazelnuts"],
    "Snacks": ["Potato Chips", "Nachos", "Roasted Peanuts", "Samosa", "Cookies",
               "Trail Mix", "Popcorn", "Murukku", "Banana Chips", "Energy Bar"],
    "Beverages": ["Cola", "Orange Juice", "Mango Lassi", "Sweet Tea", "Coffee with Milk",
                  "Coconut Water", "Chocolate Milkshake", "Lemonade", "Iced Coffee", "Fruit Smoothie"],
    "Desserts": ["Gulab Jamun", "Ice Cream", "Chocolate Cake", "Rasgulla", "Donut",
                 "Brownie", "Jalebi", "Kheer", "Pastry", "Cupcake"],
    "Fast Food": ["Veg Burger", "Cheese Pizza Slice", "French Fries", "Chicken Burger",
                  "Veg Sandwich", "Fried Chicken", "Hot Dog", "Veg Wrap", "Nachos with Cheese", "Pav Bhaji"],
}


def atwater_calories(protein, carbs, fat, fiber):
    """Ground-truth energy estimate per 100 g (Atwater factors)."""
    return protein * 4.0 + carbs * 4.0 + fat * 9.0 + fiber * 2.0


def create_dataset(n_records=1000, seed=42, path=DATASET_PATH):
    """Activity 1 - Dataset Creation: build the food nutrition CSV dataset."""
    rng = np.random.default_rng(seed)
    categories = list(CATEGORY_PROFILES.keys())
    rows = []

    for i in range(n_records):
        category = categories[i % len(categories)]
        profile = CATEGORY_PROFILES[category]

        protein = rng.uniform(*profile["protein"])
        carbs = rng.uniform(*profile["carbs"])
        fat = rng.uniform(*profile["fat"])
        fiber = rng.uniform(*profile["fiber"])
        sugar = rng.uniform(*profile["sugar"])
        serving = rng.uniform(*profile["serving"])

        kcal_per_100g = atwater_calories(protein, carbs, fat, fiber)
        kcal_per_100g *= rng.normal(1.0, 0.03)          # small real-world noise
        calories = max(0.0, kcal_per_100g * serving / 100.0)

        name = FOOD_NAMES[category][i % len(FOOD_NAMES[category])]
        rows.append({
            "Food Name": name,
            "Category": category,
            "Serving Size (g)": round(serving, 1),
            "Protein (g)": round(protein, 1),
            "Carbohydrates (g)": round(carbs, 1),
            "Total Fat (g)": round(fat, 1),
            "Dietary Fiber (g)": round(fiber, 1),
            "Sugars (g)": round(sugar, 1),
            TARGET_COL: round(calories, 2),
        })

    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df


def load_dataset(path=DATASET_PATH):
    """Activity 2 - Data Loading: load with Pandas and check required columns."""
    if not os.path.exists(path):
        create_dataset(path=path)
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df


def clean_dataset(df):
    """Activity 3 - Data Cleaning: infinite -> NaN -> drop, numeric coercion,
    and range validation on the numeric columns."""
    df = df.replace([np.inf, -np.inf], np.nan).dropna().copy()

    numeric_cols = FEATURE_COLS + [TARGET_COL]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=numeric_cols)

    df = df[(df["Serving Size (g)"] > 0) & (df["Serving Size (g)"] <= 1000)]
    df = df[(df["Protein (g)"].between(0, 100)) &
            (df["Carbohydrates (g)"].between(0, 100)) &
            (df["Total Fat (g)"].between(0, 100)) &
            (df["Dietary Fiber (g)"].between(0, 40)) &
            (df["Sugars (g)"].between(0, 100))]
    df = df[df[TARGET_COL].between(0, 2000)]
    return df.reset_index(drop=True)


def train(df):
    """Activity 4/5/6/7 - Feature selection, Random Forest training,
    evaluation, cross-validation and model saving."""
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = mean_absolute_error(y_test, y_pred)

    cv_r2 = cross_val_score(model, X, y, cv=5, scoring="r2", n_jobs=-1)
    cv_mae = -cross_val_score(model, X, y, cv=5,
                              scoring="neg_mean_absolute_error", n_jobs=-1)

    importances = pd.Series(model.feature_importances_,
                            index=FEATURE_COLS).sort_values(ascending=False)

    joblib.dump(model, MODEL_PATH)

    metrics = {
        "r2": r2, "rmse": rmse, "mae": mae,
        "cv_r2_mean": cv_r2.mean(), "cv_r2_std": cv_r2.std(),
        "cv_mae_mean": cv_mae.mean(), "cv_mae_std": cv_mae.std(),
        "importances": importances,
        "n_train": len(X_train), "n_test": len(X_test),
    }
    return model, metrics


def main():
    print("=" * 60)
    print("  FOOD CALORIE PREDICTION SYSTEM - MODEL TRAINING")
    print("=" * 60)

    if not os.path.exists(DATASET_PATH):
        print("\n[1] Dataset Creation -> food_calorie_dataset_1000.csv")
        create_dataset()
    df = load_dataset()
    print(f"\n[2] Data Loading     -> {len(df)} records loaded")

    df = clean_dataset(df)
    print(f"[3] Data Cleaning    -> {len(df)} valid records retained")

    print("\n[4] Model Training   -> RandomForestRegressor "
          "(n_estimators=300, max_depth=10, min_samples_leaf=2)")
    _, metrics = train(df)

    print("\n[5] Model Evaluation (hold-out 80/20 split)")
    print(f"    Train records      : {metrics['n_train']}")
    print(f"    Test records       : {metrics['n_test']}")
    print(f"    R2 Score           : {metrics['r2']:.4f}")
    print(f"    RMSE               : {metrics['rmse']:.2f} kcal")
    print(f"    MAE                : {metrics['mae']:.2f} kcal")

    print("\n[6] 5-Fold Cross-Validation")
    print(f"    CV R2              : {metrics['cv_r2_mean']:.4f} "
          f"(+/- {metrics['cv_r2_std']:.4f})")
    print(f"    CV MAE             : {metrics['cv_mae_mean']:.2f} kcal "
          f"(+/- {metrics['cv_mae_std']:.2f})")

    print("\n[7] Feature Importance")
    for name, imp in metrics["importances"].items():
        print(f"    {name:<22}: {imp:.4f}")

    print(f"\n[8] Model saved to   -> {MODEL_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
