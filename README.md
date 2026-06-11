# Drug Discovery Learning Platform

An interactive computational pipeline for learning drug discovery, from target identification through regulatory approval.

## Architecture

```
backend/   FastAPI (Python) — pipeline logic, PubMed + Claude API integration
frontend/  React + Vite + Tailwind — interactive UI
```

Pipeline stages (each stage feeds output into the next):
1. **Target Identification** — literature mining via PubMed + Claude NER
2. **Hit Discovery** — virtual screening _(coming soon)_
3. **Lead Optimization** — ADMET prediction _(coming soon)_
4. **Preclinical** _(coming soon)_
5. **Clinical Trials** _(coming soon)_
6. **Regulatory Approval** _(coming soon)_

## Setup

### 1. API key

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs available at http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Docker (optional)

```bash
cp .env.example .env  # add your key
docker-compose up
```

## Running tests

```bash
cd backend
pytest tests/
```

## Key files

| File | Purpose |
|------|---------|
| `backend/services/pubmed_client.py` | PubMed E-utilities wrapper (esearch + efetch) |
| `backend/services/claude_client.py` | Anthropic SDK wrapper, NER/relation extraction prompts |
| `backend/services/ensemble.py` | Consensus scoring when multiple methods are run |
| `backend/pipeline/target_identification/literature_mining.py` | Stage 1 orchestration |
| `frontend/src/context/PipelineContext.tsx` | Global state, inter-stage data passing |
