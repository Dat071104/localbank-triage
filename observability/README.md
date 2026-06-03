# Local Observability

Phase 13 adds a small local Prometheus/Grafana stack for debugging the local triage app. It is optional and uses the `observability` compose profile.

PowerShell:

```powershell
docker compose -f docker-compose.yml -f docker-compose.observability.yml --profile observability config --quiet
docker compose -f docker-compose.yml -f docker-compose.observability.yml --profile observability up -d prometheus grafana
```

Prometheus scrapes `/metrics` from classifier-service, urgency-service, rag-service, llm-service, and api-gateway. The current metrics are intentionally lightweight:

- `service_request_count_total`
- `service_error_count_total`
- `service_request_latency_seconds_sum`
- `classifier_classify_seconds`
- `urgency_score_seconds`
- `rag_search_seconds`
- `llm_generate_seconds`
- `critical_ticket_count_total`
- `gateway_downstream_request_seconds`
- `worker_pipeline_seconds`
- `draft_validation_failures_total`

Grafana runs at `http://localhost:3000` with local dev credentials from `.env.example`. Generated Prometheus/Grafana data directories are ignored and must not be committed.
