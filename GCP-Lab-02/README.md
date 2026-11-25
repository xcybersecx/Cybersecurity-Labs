# GCP Lab 02: Project Administration, IAM and Budget Automation

**Date:** 25 November 2026  
**Environment:** Ubuntu in Oracle VirtualBox; Google Cloud CLI 594.0.1; Google Cloud Console  
**Status:** Completed project administration and dry-run integration testing. Automated shutdown not deployed.

## Objective
Configure a dedicated Google Cloud training project, establish billing monitoring, practice identity and access management (IAM), and prototype an event-driven budget response without interrupting live services.

## 1. Project administration
After authenticating with the Google Cloud CLI, I created a dedicated lab project and used the Alpha Interactive shell to practice listing, creating, switching, deleting and restoring projects. A separate practice project was restored and verified as ACTIVE.

Representative commands (identifiers replaced with placeholders):
```bash
gcloud projects list
gcloud projects create PRACTICE_PROJECT_ID --name="Practice Project"
gcloud config set project PRACTICE_PROJECT_ID
gcloud config get-value project
gcloud config set project LAB_PROJECT_ID
gcloud projects delete PRACTICE_PROJECT_ID
gcloud projects undelete PRACTICE_PROJECT_ID
gcloud projects describe PRACTICE_PROJECT_ID
```

## 2. Billing and cost monitoring
The console displayed a $300 welcome credit and 90 days remaining, following a $30 prepayment. Reported usage cost was $0 at the time of inspection. An inconsistent expired-trial banner appeared during setup; the promotional credit display alone does not resolve that inconsistency.

Two monthly $5 alert budgets were created:
- Cloud Lab Budget: account-wide.
- Cloud Lab Automation Budget: restricted to the training project, with a Pub/Sub topic selected.

Actual spending thresholds: 50% ($2.50), 90% ($4.50), 100% ($5). Savings exclusions were configured to monitor costs before applicable selected credits. Email alerts were enabled.

The training project was linked to the existing billing account. CLI verification returned `billingEnabled: true`. Budget alerts are not hard spending caps, and reported costs can lag.

## 3. APIs and region
```bash
gcloud services enable compute.googleapis.com
gcloud config set compute/region us-central1
gcloud config get-value compute/region
gcloud services enable cloudbilling.googleapis.com
gcloud services enable pubsub.googleapis.com
```
All three API enablement operations completed successfully; the default region returned `us-central1`. No cloud VM was deployed during this exercise.

## 4. Identity and access management
```bash
gcloud iam service-accounts create budget-alert --display-name="Budget Alert Service Account"
gcloud iam service-accounts list
gcloud projects add-iam-policy-binding LAB_PROJECT_ID --member="serviceAccount:budget-alert@LAB_PROJECT_ID.iam.gserviceaccount.com" --role="roles/billing.projectManager"
```
The service account was created and the project IAM policy update succeeded. The role is scoped to the lab project, but remains privileged and should be reviewed or removed when not needed. No service account keys were generated during the demonstrated steps.

**Security observation:** The default Compute Engine service account was listed with the broad Editor role. A future hardening exercise should assess required permissions before reducing them.

## 5. Pub/Sub messaging
```bash
gcloud pubsub topics create budget-alerts
gcloud pubsub subscriptions create budget-alerts-test --topic=budget-alerts
gcloud pubsub topics publish budget-alerts --message="Hello from my cloud security lab"
gcloud pubsub subscriptions pull budget-alerts-test --auto-ack --limit=1
gcloud pubsub subscriptions delete budget-alerts-test
```
The test message was retrieved with ACK_STATUS: SUCCESS. The temporary subscription was deleted; the topic was retained.

## 6. Python dry-run prototype
A local working directory was created and main.py developed using Nano. The prototype decodes Base64 message data, parses JSON, validates finite numeric values and a positive budget, and compares cost against budget. It prints a hypothetical response rather than calling the billing API.

```python
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
    decoded = base64.b64decode(event["message"]["data"])
    check_budget(json.loads(decoded))

if __name__ == "__main__":
    for cost in [2, 5, 6]:
        print(f"\nTesting spending of ${cost}")
        payload = {"costAmount": cost, "budgetAmount": 5}
        encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        process_message({"message": {"data": encoded}})
```

## 7. Integration and validation
A fresh temporary subscription was created and synthetic billing data published to the actual cloud topic:
```bash
gcloud pubsub subscriptions create budget-alerts-test --topic=budget-alerts
gcloud pubsub topics publish budget-alerts --message='{"costAmount":6,"budgetAmount":5}'
gcloud pubsub subscriptions pull budget-alerts-test --auto-ack --limit=1 --format=json > message.json
python3 -c 'import json; from main import process_message; process_message(json.load(open("message.json"))[0])'
gcloud pubsub subscriptions delete budget-alerts-test
```

| Test | Expected | Observed |
|---|---|---|
| $2 / $5 | Within budget | PASS |
| $5 / $5 | Simulated shutdown | PASS |
| $6 / $5 | Simulated shutdown | PASS |
| $6 / $0 | Invalid budget error | PASS |
| Encoded synthetic payloads | Correct threshold decisions | PASS |
| Actual Pub/Sub delivery of synthetic $6 / $5 message | Decode and simulate shutdown | PASS |
| Temporary subscription cleanup | Deleted | PASS |

The integration test was manually triggered. It did not verify delivery of a genuine Cloud Billing notification.

## 8. Troubleshooting
- VirtualBox clipboard integration was restored using guest utilities and VBoxClient.
- Compute Engine API was initially disabled; the interactive prompt did not complete. Direct enablement from the regular Ubuntu terminal succeeded.
- Cloud Billing API returned HTTP 429 RESOURCE_EXHAUSTED during an earlier request. A later billing description succeeded; the precise cause of the rate limit was not established.

## 9. Architecture and limitations
```
Configured budget -> Pub/Sub topic -> future cloud event handler
                            |
                   temporary pull subscription (deleted)
                            |
                   local JSON -> Python dry run (verified)
```
No Cloud Run function was deployed, no billing shutdown occurred, and continuous automated enforcement is not operational. A requirements file was suggested but its creation was not confirmed. Before deployment, validate authentic budget metadata, project scope, currency, malformed inputs, duplicate/stale events and access controls; assess deployment costs and the inconsistent trial status. Automatic billing disconnection can interrupt services and is not an exact spending cap.

## Evidence
Screenshots were captured during the exercise. Public versions should redact personal email addresses, billing account identifiers, project numbers, acknowledgement IDs and other unnecessary identifiers. Raw message.json and payment screenshots should not be uploaded. Screenshots are not included in this initial text entry.

## Learning outcomes
Project lifecycle management, CLI configuration, API enablement, cloud billing governance, IAM role binding, asynchronous messaging, JSON/Base64 processing, boundary testing, input validation and manual cloud-to-local integration testing.
