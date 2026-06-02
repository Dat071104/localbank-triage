# urgency-service

Hybrid urgency scoring service for LocalBank-Triage.

## Install

```powershell
python -m pip install -r .\services\urgency-service\requirements.txt
```

## Run API

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --app-dir .\services\urgency-service
```

## Run Tests

```powershell
python -m pytest .\services\urgency-service\tests\test_urgency_rules.py -q
python -m pytest .\services\urgency-service\tests\test_urgency_api.py -q
```

## Scoring Model

`urgency_score = 0.40 * business_risk_score + 0.25 * urgency_classifier_score + 0.15 * intent_severity_score + 0.10 * red_flag_rule_score + 0.10 * sentiment_escalation_score`

Critical override rules take precedence over the weighted baseline for OTP leakage, unauthorized transactions with amount signals, lost-card money loss, and hacked-account access issues.
