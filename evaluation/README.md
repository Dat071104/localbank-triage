# Final Evaluation

Phase 15 provides a rerunnable synthetic/contract evaluation for LocalBank-Triage. Reports can be written under ignored `artifacts/evaluation/`.

PowerShell:

```powershell
python -m pytest evaluation\tests -q
python -m evaluation.final.run_final_evaluation
python -m evaluation.final.production_readiness_check
python -m evaluation.final.production_readiness_check --performance
python -m evaluation.final.production_readiness_check --real-llm-smoke
```

The readiness checker returns `PARTIAL PASS` unless real-stack browser smoke and real local LLM smoke have credible runtime evidence. Synthetic/contract metrics are useful release gates, not proof of production accuracy against live customers or a broad labeled dataset.
