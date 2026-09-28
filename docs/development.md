# Sarthi Development & Testing Guide

This guide covers local environment setup, running the FastAPI backend and React frontend, executing the automated test suite, and validating the [Hindsight](https://github.com/vectorize-io/hindsight) memory engine.

> **Publishing note**: When publishing the article and LinkedIn post, tag Code.in as required by the submission guide.

---

## 1. Prerequisites

- **Python**: 3.10+ (tested with Python 3.10 through 3.14)
- **Node.js**: 18+ and npm
- **Hindsight Account**: API key and base URL from [Hindsight](https://hindsight.vectorize.io/)
- **Azure OpenAI Account**: Deployment of GPT-4o-mini (or compatible model)

---

## 2. Environment Configuration

Copy the example environment configuration in `backend/.env.example` to `backend/.env`:

```bash
cd backend
cp .env.example .env
```

Configure the following environment variables in `backend/.env`:

```ini
# Hindsight Long-Term Memory Service
HINDSIGHT_API_KEY=your-hindsight-api-key-here
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=sarthi
HINDSIGHT_TIMEOUT=30.0

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Azure Speech (Optional for text-only development)
AZURE_SPEECH_KEY=your-azure-speech-key-here
AZURE_SPEECH_REGION=eastus
AZURE_SPEECH_ENDPOINT=https://eastus.api.cognitive.microsoft.com/

# Security
SECRET_KEY=your-jwt-secret-key-here
```

> **Security Reminder**: Never commit `.env` or sensitive credentials. The repository `.gitignore` automatically excludes `.env` files.

---

## 3. Backend Setup

### 3.1 Create Virtual Environment & Install Dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Synchronize Authoritative Agricultural Ground Truth

Populate the local database with 702 districts, 702 soil fertility baselines, 22 ICAR crops, 13 multi-season crop calendars, Agmarknet mandi rates, and IMD advisories:

```bash
python -m ingestion.run_all_sync
```

### 3.3 Start FastAPI Server

```bash
uvicorn main:app --reload --port 8000
```

FastAPI interactive Swagger documentation is available at:
`http://localhost:8000/docs`

---

## 4. Frontend Setup

### 4.1 Install Dependencies & Start Vite Server

```bash
cd frontend
npm install
npm run dev
```

The web application will be live at `http://localhost:5173`.

### 4.2 Validate Production Build

```bash
npm run build
```

This compiles client assets using Vite and TailwindCSS into `dist/`.

---

## 5. Running Tests

### 5.1 Run Complete Backend Test Suite (51 Tests)

```bash
cd backend
PYTHONPATH=. .venv/bin/pytest -v tests/
```

Test suites included:
- `tests/test_hindsight_memory.py`: 12 tests verifying Hindsight configuration, taxonomy models, tenant isolation, credit deduplication, and error boundaries.
- `tests/test_memory_api.py`: 4 tests validating memory endpoints and JWT auth.
- `tests/test_phase3_phase4.py`: 16 tests validating targeted recall, precedence policy, memory influence metadata, feedback learning loop, and retain resilience.
- `tests/test_hindsight_live.py`: 3 live connectivity and multi-type recall tests against Hindsight Cloud.
- `tests/test_agri_recovery.py`: 14 tests validating Soil Health Card, ICAR, crop calendar, and market rate data serving.
- `tests/test_auth_azure_tables.py`: 2 tests validating user registration and demo farmer authentication.

### 5.2 Run Multi-Session End-to-End Validation

Execute the standalone multi-session sequence script:

```bash
PYTHONPATH=. .venv/bin/python validate_e2e_flow.py
```

This verifies the 8-step multi-session flow:
1. Retaining a hard water constraint
2. Confirming the constraint shapes recommendation 1
3. Recording conversational failure feedback ("tomato failed due to water shortage")
4. Confirming outcome memory is persisted
5. Starting a new session and confirming changed recommendation (deprioritizing tomato)
6. Verifying structured memory influence explanation
7. Explaining "Why this recommendation?"
8. Confirming strict cross-farmer memory isolation

---

## 6. Official External Resources

- [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight)
- [Hindsight documentation](https://hindsight.vectorize.io/)
- [Vectorize's explanation of agent memory](https://vectorize.io/what-is-agent-memory)
