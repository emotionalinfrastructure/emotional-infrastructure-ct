# Developer Guide

## Prereqs
- Python 3.11
- Docker + Docker Compose (optional)

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run locally
```bash
python app.py
# or via compose (issuer, server, prometheus, grafana)
docker compose up
```

## Tests
```bash
pytest -v
```

## Project structure
```
issuer.py   # token issuance
server.py   # validation + revocation endpoints
app.py      # API entry
docs/       # developer + architecture docs
tests/      # unit/functional tests
```
