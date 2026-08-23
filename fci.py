def classify_food(calories):
    calories = max(0.0, float(calories))
    if calories < 150.0:
        return "Low Calorie", "Low Caution"
    if calories <= 350.0:
        return "Moderate Calorie", "Medium Caution"
    return "High Calorie", "High Caution"


def generate_recommendation(caution_level, serving_size, protein, carbs,
                            fat, fiber=None, sugar=None):
    serving_size = float(serving_size)
    protein = float(protein)
    carbs = float(carbs)
    fat = float(fat)
    fiber = None if fiber is None else float(fiber)
    sugar = None if sugar is None else float(sugar)

    # Atwater energy hint (kcal per serving) used only to gate flags.
    kcal_hint = (protein * 4 + carbs * 4 + fat * 9 + (fiber or 0.0) * 2) \
        * serving_size / 100.0
    energy_dense = fat > 15 or (sugar is not None and sugar > 15)

    issues = []
    if fat > 15:
        issues.append("choose a smaller portion or a low-fat preparation method")
    if sugar is not None and sugar > 15:
        issues.append("limit added/free sugar intake for the rest of the day")
    if fiber is not None and fiber < 2 and energy_dense:
        issues.append("pair with fiber-rich foods such as vegetables or whole grains")
    if protein < 5 and energy_dense:
        issues.append("pair with a lean protein source for better satiety")
    if serving_size > 250 and kcal_hint > 350:
        issues.append("watch the portion size, this is a large energy-dense serving")

    if not issues:
        if caution_level == "Low Caution":
            return ("Enjoy freely; this food fits well into most balanced, "
                    "calorie-conscious diets.")
        if caution_level == "High Caution":
            return ("This serving is calorie-dense; limit the portion size "
                    "and how often you eat it, and balance the rest of "
                    "your day's meals around it.")
        return ("Fits into a balanced diet; keep portions consistent with "
                "your daily calorie goal.")

    if caution_level == "High Caution":
        prefix = "Priority actions: "
    elif caution_level == "Medium Caution":
        prefix = "Recommended actions: "
    else:
        prefix = "Continue monitoring; "

    return prefix + "; ".join(issues) + "."
