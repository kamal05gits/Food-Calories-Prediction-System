"""
UNIT TESTS — Food Calories Prediction System
=============================================
Tests individual functions in complete isolation (no API, no files, no network).

Covers:
    fci.classify_food()                - calorie class / caution level logic
    fci.generate_recommendation()      - recommendation text generation
    functions.calculate_calories()     - Atwater rule-based estimate
    functions.calculate_calorie_level()- rule-based level mapping
    main.validate_inputs()             - input validation rules

Run:  python unit_test.py
"""

import sys

import main
from fci import classify_food, generate_recommendation
from functions import calculate_calories, calculate_calorie_level

RESULTS = []


def record(test_id, operation, expected, actual, passed):
    RESULTS.append({
        "Test ID": test_id,
        "Operation": operation,
        "Expected": expected,
        "Actual": actual,
        "Status": "Pass" if passed else "Fail",
    })


def report():
    print("\n### UNIT TEST RESULTS\n")
    print("| Test ID | Operation | Expected | Actual | Status |")
    print("|:---|:---|:---|:---|:---:|")
    for r in RESULTS:
        print(f"| {r['Test ID']} | {r['Operation']} | {r['Expected']} | {r['Actual']} | {r['Status']} |")
    passed = sum(1 for r in RESULTS if r["Status"] == "Pass")
    print(f"\n**{passed}/{len(RESULTS)} unit tests passed.**\n")
    return passed == len(RESULTS)


VALID_INPUT = {
    "Food Name": "Grilled Chicken",
    "Serving Size (g)": "150", "Protein (g)": "28",
    "Carbohydrates (g)": "0", "Total Fat (g)": "3.6",
    "Dietary Fiber (g)": "0", "Sugars (g)": "0",
}


def run():
    # UT-01 low calorie classification
    r = classify_food(120)
    record("UT-01", "classify_food(120)", "Low Calorie / Low Caution", str(r),
           r == ("Low Calorie", "Low Caution"))

    # UT-02 moderate calorie classification
    r = classify_food(250)
    record("UT-02", "classify_food(250)", "Moderate Calorie / Medium Caution", str(r),
           r == ("Moderate Calorie", "Medium Caution"))

    # UT-03 high calorie classification
    r = classify_food(480)
    record("UT-03", "classify_food(480)", "High Calorie / High Caution", str(r),
           r == ("High Calorie", "High Caution"))

    # UT-04 classification boundary values
    checks = {
        149.99: ("Low Calorie", "Low Caution"),
        150.0:  ("Moderate Calorie", "Medium Caution"),
        350.0:  ("Moderate Calorie", "Medium Caution"),
        350.01: ("High Calorie", "High Caution"),
        0.0:    ("Low Calorie", "Low Caution"),
        -50.0:  ("Low Calorie", "Low Caution"),   # negative is clamped to 0
    }
    ok = all(classify_food(k) == v for k, v in checks.items())
    record("UT-04", "classify_food() boundaries (149.99/150/350/350.01/0/-50)",
           "All boundary values classify correctly", "All correct" if ok else "Boundary mismatch", ok)

    # UT-05 recommendation: high caution + high fat + high sugar
    txt = generate_recommendation("High Caution", 90, 4.2, 52.0, 22.5, 1.8, 38.0)
    ok = txt.startswith("Priority actions") and "portion" in txt and "sugar" in txt
    record("UT-05", "generate_recommendation(high-fat + high-sugar dessert)",
           "'Priority actions...' mentioning portion and sugar", txt[:80] + "...", ok)

    # UT-06 recommendation: low caution food (apple)
    txt = generate_recommendation("Low Caution", 180, 0.3, 13.8, 0.2, 2.4, 10.4)
    record("UT-06", "generate_recommendation(low-caution apple)",
           "Positive 'Enjoy freely' message", txt, "Enjoy freely" in txt)

    # UT-07 recommendation: medium caution food (chicken)
    txt = generate_recommendation("Medium Caution", 150, 28.0, 0.0, 3.6, 0.0, 0.0)
    record("UT-07", "generate_recommendation(medium-caution chicken)",
           "'balanced diet' message", txt, "balanced diet" in txt)

    # UT-08 Atwater rule-based calculation
    kcal = calculate_calories(10, 10, 5, 5, 200)
    level = calculate_calorie_level(kcal)
    ok = abs(kcal - 270.0) < 0.01 and level == "Moderate Calorie"
    record("UT-08", "calculate_calories(10,10,5,5,200) + calculate_calorie_level()",
           "270.0 kcal -> Moderate Calorie", f"{kcal:.2f} kcal -> {level}", ok)

    # UT-09 validate_inputs: complete valid record
    data, err = main.validate_inputs(dict(VALID_INPUT))
    record("UT-09", "validate_inputs(complete valid record)", "Accepted, no error",
           "Accepted" if (data is not None and err is None) else f"Error: {err}",
           data is not None and err is None)

    # UT-10 validate_inputs: empty mandatory field
    _, err = main.validate_inputs({**VALID_INPUT, "Food Name": ""})
    record("UT-10", "validate_inputs(empty Food Name)", "'all input fields' error",
           f"Error: {err}", err is not None and "all input fields" in err)

    # UT-11 validate_inputs: non-numeric nutrient value
    _, err = main.validate_inputs({**VALID_INPUT, "Protein (g)": "abc"})
    record("UT-11", "validate_inputs(Protein='abc')", "'numerical' error",
           f"Error: {err}", err is not None and "numerical" in err)

    # UT-12 validate_inputs: out-of-range nutrient (fat = 150)
    _, err = main.validate_inputs({**VALID_INPUT, "Total Fat (g)": "150"})
    record("UT-12", "validate_inputs(Total Fat=150)", "'between 0 and 100' error",
           f"Error: {err}", err is not None and "between 0 and 100" in err)

    # UT-13 validate_inputs: invalid serving size (0 g)
    _, err = main.validate_inputs({**VALID_INPUT, "Serving Size (g)": "0"})
    record("UT-13", "validate_inputs(Serving Size=0)", "'between 1 and 1000' error",
           f"Error: {err}", err is not None and "between 1 and 1000" in err)

    return report()


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
