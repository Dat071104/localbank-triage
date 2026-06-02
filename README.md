# LocalBank-Triage

LocalBank-Triage is a local-first support triage app for Vietnamese banking and fintech customer service teams.

The goal is to help internal staff classify customer tickets, detect urgent cases, retrieve relevant internal policy guidance, and prepare human-reviewed response drafts without sending sensitive customer data to external AI APIs.

## Planned Features

- Local staff login with employee credentials
- Role-based access control for agents, supervisors, auditors, and admins
- Vietnamese ticket classification
- Urgency scoring for fraud, OTP leakage, card loss, account access, and transaction disputes
- Local policy retrieval using RAG
- Human-reviewed response draft generation
- Dockerized local deployment

## Current Status

Project setup is in progress.

## Tech Direction

- FastAPI for backend services
- SQLite for local staff authentication
- PostgreSQL for product workflow data
- Qdrant for vector search
- PhoBERT for Vietnamese classification
- Qwen2.5-3B for local draft generation
- React / Tauri for the app interface
- Docker Compose for local deployment

## Notes

This project is built as a local-first AI engineering portfolio project. Sensitive customer text should remain inside the local environment.
