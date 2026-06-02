# classifier-service

Classifier data pipeline and rule-based Vietnamese ticket classification service for LocalBank-Triage.

## Phase 2 Dataset Pipeline

The pipeline keeps all raw and prepared datasets under ignored `data/` paths. If an external banking dataset is unavailable, the repo falls back to a committed tiny synthetic fixture for tests and a synthetic raw dataset generator for local runs.

## Install

```powershell
python -m pip install -r .\services\classifier-service\requirements.txt
```

## Generate Raw Demo Data

```powershell
python .\services\classifier-service\data_pipeline\download_data.py --output data\raw\classifier\synthetic_tickets.jsonl
```

## Prepare Dataset

```powershell
python .\services\classifier-service\data_pipeline\prepare_dataset.py --input data\raw\classifier\synthetic_tickets.jsonl --output data\processed\classifier\prepared_tickets.jsonl
```

## Run Tests

```powershell
python -m pytest .\services\classifier-service\tests\test_data_pipeline.py -q
```
