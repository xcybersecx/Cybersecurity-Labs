import base64
import json
import math


def check_budget(data):
    cost = float(data["costAmount"])
    budget = float(data["budgetAmount"])

    if not math.isfinite(cost) or not math.isfinite(budget):
        raise ValueError("Invalid spending data")

    if budget <= 0:
        raise ValueError("Invalid budget amount")

    print(f"Current spending: ${cost:.2f}")
    print(f"Budget limit: ${budget:.2f}")

    if cost >= budget:
        print("DRY RUN: Billing would be disabled.")
    else:
        print("Spending is within budget.")


def process_message(event):
    encoded = event["message"]["data"]
    decoded = base64.b64decode(encoded)
    data = json.loads(decoded)
    check_budget(data)


if __name__ == "__main__":
    for cost in [2, 5, 6]:
        print(f"\nTesting spending of ${cost}")

        payload = {
            "costAmount": cost,
            "budgetAmount": 5
        }

        encoded = base64.b64encode(
            json.dumps(payload).encode()
        ).decode()

        event = {"message": {"data": encoded}}

        process_message(event)
