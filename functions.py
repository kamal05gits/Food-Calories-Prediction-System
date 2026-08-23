def get_food_data():
    food_name = input("Enter Food Name: ")

    category = input("Enter Food Category (e.g. Fruits, Dairy, Snacks): ")
    serving_size = float(input("Enter Serving Size (g): "))
    protein = float(input("Enter Protein (g per 100 g): "))
    carbs = float(input("Enter Carbohydrates (g per 100 g): "))
    fat = float(input("Enter Total Fat (g per 100 g): "))
    fiber = float(input("Enter Dietary Fiber (g per 100 g): "))
    sugar = float(input("Enter Sugars (g per 100 g): "))

    food_data = {
        "food_name": food_name,
        "category": category,
        "serving_size": serving_size,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "fiber": fiber,
        "sugar": sugar,
    }

    return food_data


def calculate_calories(protein, carbs, fat, fiber, serving_size):
    kcal_per_100g = (protein * 4) + (carbs * 4) + (fat * 9) + (fiber * 2)
    return kcal_per_100g * serving_size / 100.0


def calculate_calorie_level(calories):
    if calories < 150:
        return "Low Calorie"
    elif calories <= 350:
        return "Moderate Calorie"
    else:
        return "High Calorie"


def display_result(food_data, calories, level):
    print("\n" + "=" * 50)
    print("        FOOD CALORIE PREDICTION RESULT")
    print("=" * 50)

    print(f"Food Name        : {food_data['food_name']}")
    print(f"Category         : {food_data['category']}")

    print(f"\nServing Size     : {food_data['serving_size']} g")
    print(f"Protein          : {food_data['protein']} g/100 g")
    print(f"Carbohydrates    : {food_data['carbs']} g/100 g")
    print(f"Total Fat        : {food_data['fat']} g/100 g")
    print(f"Dietary Fiber    : {food_data['fiber']} g/100 g")
    print(f"Sugars           : {food_data['sugar']} g/100 g")

    print("\nEstimated Calories :", round(calories, 2), "kcal")
    print("Calorie Level      :", level)

    if level == "Low Calorie":
        print("Diet Caution     : Low")
        print("Recommendation   : Enjoy freely; fits most calorie-conscious diets.")
    elif level == "Moderate Calorie":
        print("Diet Caution     : Medium")
        print("Recommendation   : Fits into a balanced diet; keep portions consistent.")
    else:
        print("Diet Caution     : High")
        print("Recommendation   : Limit frequency and reduce the portion size.")

    print("=" * 50)


if __name__ == "__main__":
    data = get_food_data()
    est_calories = calculate_calories(
        data["protein"], data["carbs"], data["fat"],
        data["fiber"], data["serving_size"]
    )
    calorie_level = calculate_calorie_level(est_calories)
    display_result(data, est_calories, calorie_level)
