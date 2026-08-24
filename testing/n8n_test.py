"""
N8N AGENT TESTS — Food Calories HIGH Alert Agent
=================================================
Black-box tests of the n8n webhook agent end-to-end:

  N8N-1  Webhook is live (production URL answers POST with JSON)
  N8N-2  HIGH-calorie food (fries)  -> alert: true  (calorie_class = "High Calorie"
         AND diet_caution_level = "High Caution")
  N8N-3  Normal food (chicken)      -> alert: false (no false alarms)
  N8N-4  Invalid payload            -> HTTP 4xx error (not a silent 200)
  N8N-5  Response echoes the food name (request/response contract)

Usage:
    python n8n_test.py                                   # tests the n8n.cloud URL below
    python n8n_test.py http://127.0.0.1:5678/webhook/food-calorie-alert   # custom URL
    N8N_WEBHOOK_URL=... python n8n_test.py

NOTE: for the agent to alert correctly, the HTTP Request node in the n8n
workflow must point at a REACHABLE deployment of api.py (/predict).
"""

import os
import sys

import requests

# Default: your n8n CLOUD production webhook URL.
# Override with an argument or the N8N_WEBHOOK_URL env var.
WEBHOOK_URL = os.environ.get(
    "N8N_WEBHOOK_URL",
    "https://kamal-05.app.n8n.cloud/webhook/calorie-prediction",
)
if len(sys.argv) > 1:
    WEBHOOK_URL = sys.argv[1]

TIMEOUT = 60

HIGH_FOOD = {"food_name": "French Fries", "serving_size": 150, "protein": 3.4,
             "carbohydrates": 41.0, "total_fat": 15.0, "dietary_fiber": 3.4, "sugars": 0.6}
LOW_FOOD = {"food_name": "Grilled Chicken Breast", "serving_size": 150, "protein": 28.0,
            "carbohydrates": 0.0, "total_fat": 3.6, "dietary_fiber": 0.0, "sugars": 0.0}
BAD_FOOD = {"food_name": "Mystery Food"}   # missing all required fields

RESULTS = []
LAST_ERROR = None


def record(test_id, operation, expected, actual, passed):
    RESULTS.append({
        "Test ID": test_id,
        "Operation": operation,
        "Expected": expected,
        "Actual": actual,
        "Status": "Pass" if passed else "Fail",
    })


def report():
    print(f"\n### N8N AGENT TEST RESULTS — {WEBHOOK_URL}\n")
    print("| Test ID | Operation | Expected | Actual | Status |")
    print("|:---|:---|:---|:---|:---:|")
    for r in RESULTS:
        print(f"| {r['Test ID']} | {r['Operation']} | {r['Expected']} | {r['Actual']} | {r['Status']} |")
    passed = sum(1 for r in RESULTS if r["Status"] == "Pass")
    print(f"\n**{passed}/{len(RESULTS)} n8n agent tests passed.**\n")
    return passed == len(RESULTS)


def post(payload):
    """POST to the webhook; returns (status_code, json_or_none, error_or_none)."""
    global LAST_ERROR
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=TIMEOUT)
        try:
            return r.status_code, r.json(), None
        except ValueError:
            return r.status_code, None, f"non-JSON body: {r.text[:120]}"
    except requests.RequestException as exc:
        LAST_ERROR = str(exc)
        return None, None, LAST_ERROR


def run():
    # N8N-1 webhook live
    code, body, err = post(HIGH_FOOD)
    if err:
        record("N8N-1", "Webhook live (POST high-calorie food)", "HTTP 200 + JSON", f"UNREACHABLE: {err[:100]}", False)
        for t, op, exp in [("N8N-2", "HIGH food triggers alert", "alert: true"),
                           ("N8N-3", "Normal food -> no alert", "alert: false"),
                           ("N8N-4", "Invalid payload -> 4xx", "HTTP 4xx"),
                           ("N8N-5", "Response echoes food name", "food_name in response")]:
            record(t, op, exp, "skipped (webhook unreachable)", False)
        return report()
    record("N8N-1", "Webhook live (POST high-calorie food)", "HTTP 200 + JSON",
           f"HTTP {code}, JSON fields={sorted(body.keys()) if body else err}", code == 200 and body is not None)

    # N8N-2 high food triggers the alert
    high_flag = bool(body and body.get("alert") is True)
    high_marker = body and (body.get("level") == "HIGH" or body.get("severity") == "HIGH"
                            or "HIGH CALORIE ALERT" in str(body.get("message", "")))
    ok = high_flag and bool(high_marker)
    actual = (f"alert={body.get('alert')}, level/severity={body.get('level') or body.get('severity')}, "
              f"message={str(body.get('message'))[:60]}...") if body else f"error: {err}"
    if body and not ok:
        actual += "  <-- NOTE: 'undefined' values mean the n8n HTTP node cannot reach the prediction API" \
            if "undefined" in str(body) else ""
    record("N8N-2", "HIGH food (fries 440 kcal) triggers the alert",
           "alert: true with HIGH level", actual, ok)

    # N8N-3 normal food does not alert
    code3, body3, err3 = post(LOW_FOOD)
    ok = code3 == 200 and body3 is not None and body3.get("alert") is False \
        and "undefined" not in str(body3)
    actual = f"alert={body3.get('alert')}, message={str(body3.get('message'))[:60]}..." if body3 else f"error: {err3}"
    record("N8N-3", "Normal food (chicken ~198 kcal) -> no false alarm",
           "alert: false with real class/level (not 'undefined')", actual, ok)

    # N8N-4 invalid payload -> 4xx (a 404 here would mean the agent itself is
    # not registered/active, which N8N-1 already flags)
    code4, body4, err4 = post(BAD_FOOD)
    ok = code4 is not None and 400 <= code4 < 500 and code4 != 404 \
        and (body4.get("error") is True or code4 == 422)
    detail = (body4.get("message") or body4.get("detail") or err4 or "")[:80] if body4 else (err4 or "")[:80]
    actual = f"HTTP {code4}, {detail}"
    record("N8N-4", "Invalid payload (missing fields) rejected",
           "HTTP 4xx (422 / error flag) from the agent, not 404", actual, ok)

    # N8N-5 response echoes food name
    ok = body is not None and body.get("food_name") == HIGH_FOOD["food_name"]
    record("N8N-5", "Response echoes the requested food name",
           f"food_name == '{HIGH_FOOD['food_name']}'", f"food_name={body.get('food_name') if body else 'n/a'}", ok)

    return report()


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
