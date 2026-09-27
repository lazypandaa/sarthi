# 🌾 Sarthi (सारथी) — AI Voice & Long-Term Memory Agricultural Assistant for Rural India

> **Sarthi** (*सारथी* — the trusted guide/companion) is an intelligent, voice-first agricultural AI assistant designed for Indian farmers. Powered by **Microsoft Azure OpenAI**, **Azure AI Speech**, and **Hindsight Long-Term Memory**, Sarthi remembers critical constraints, past crop outcomes, and farmer corrections across seasons to deliver hyper-personalized, adaptive farming intelligence in 9 Indian languages.

[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.10%2B-blue)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-61dafb)](https://reactjs.org/)
[![Azure](https://img.shields.io/badge/Cloud-Microsoft%20Azure-0078d4)](https://azure.microsoft.com/)
[![Hindsight](https://img.shields.io/badge/Memory-Hindsight%20AI-10b981)](https://hindsight.vectorize.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚜 The Problem

Over **120 million smallholder farmers in India** make high-stakes agricultural decisions each season. However:
1. **Stateless AI Fails Farmers**: Conventional chatbots treat every interaction as day one. They forget that a farmer's borewell runs dry by March, that their soil suffered tomato wilt last season, or that they lack capital for synthetic fertilizers.
2. **The Digital & Language Divide**: Over 65% of rural farmers face literacy or English-language barriers, preventing adoption of standard web and mobile dashboards.
3. **No Closed-Loop Learning**: Recommendations are rarely tracked against real farm outcomes or farmer feedback. When an advice fails, the assistant repeats the exact same mistake next season.

---

## 💡 The Sarthi Solution

**Sarthi** bridges this gap by combining **natural voice communication** in regional languages with an **adaptive, long-term memory engine**:

- 🗣️ **Multilingual Voice & WhatsApp**: Native voice input/output across 9 Indian languages and direct access via WhatsApp.
- 🧠 **Durable Farm Memory (Hindsight)**: Selectively captures operational constraints, verified soil observations, and season outcomes without storing conversational fluff.
- 🎯 **Memory-Aware Recommendation Engine**: Prioritizes current farm realities and user corrections over generic agronomic defaults.
- 🔄 **Autonomous Learning Loop**: Automatically updates memory when farmers report crop successes, yield failures, or corrections.
- 📊 **Transparent "Why" UI**: Displays exact memories that influenced each recommendation and tracks how system advice evolves over time.

---

## ✨ Core Pillars & Features

### 1. 🧠 Long-Term Semantic Memory (Phases 1 & 2)
Powered by **Hindsight**, Sarthi stores durable facts in an 8-category domain taxonomy:
- **`profile`**: Soil type (black, red, loamy), landholding size, location coordinates.
- **`preference`**: Organic preference, traditional seeds, preferred mandi markets.
- **`constraint`**: Critical limits (e.g., *borewell runs 2 hours/day*, *labor shortage in harvest*).
- **`crop_history`**: Past seasons, rotation cycles, historical yields.
- **`recommendation`**: Record of past advice linked by unique recommendation IDs.
- **`correction`**: Explicit farmer corrections that override past assumptions.
- **`outcome`**: Real-world harvest results, crop health reports, profit/loss feedback.
- **`incident`**: Frost events, pest outbreaks, localized flooding.

*Zero Data Leakage*: Every memory is strictly isolated at the `farmer_id` tenant level. Errors in cloud memory fail gracefully without crashing the assistant.

### 2. 🎯 Memory-Aware Recommendation & Transparent Reasoning (Phase 3)
When answering queries like *"What should I plant this season?"*:
- Sarthi recalls relevant durable memories (constraints, failures, preferences).
- Applies a **Precedence Policy**: Verified recent constraints and farmer corrections supersede generic agronomic heuristics.
- Generates **Memory Influence Metadata**:
  ```json
  {
    "type": "constraint",
    "summary": "Farmer has limited irrigation and depends purely on sparse rainfall.",
    "impact": "Prioritized drought-tolerant millets and warned against water-intensive crops."
  }
  ```
- Farmers can tap **"Why this recommendation?"** to see the transparent rationale behind every suggestion.

### 3. 🔄 Continuous Learning & Outcome Loop (Phase 4)
- **Structured Feedback**: Farmers rate advice (Helpful/Unhelpful) and log season harvest outcomes.
- **Direct Corrections**: Farmers correct outdated assumptions (e.g., *"I installed drip irrigation last month"*), immediately invalidating stale constraints.
- **Conversational Learning**: Automatically extracts durable facts from natural chat transcripts without duplicating existing memories.

### 4. 🖥️ Memory & Reasoning UI (Phase 5)
- **"What I Remember"**: Clean 4-card grid (Profile, Constraints & Preferences, Past Crop History, Learned From Feedback) with fact deletion controls.
- **"Teach Sarthi"**: Directly submit operational constraints, water limits, or crop observations.
- **"How Advice Has Evolved"**: Timeline showing what triggered a change, what was remembered, and the resulting system impact.
- **"Recommendation History"**: Auditable log of all past advice, associated influence tags, and farmer outcomes.

### 5. 🌦️ Real-Time Agricultural Data
- **Live Weather Alerts**: Hyperlocal weather forecasting and monsoon advisories.
- **Mandi Market Prices**: Real-time commodity rates from local APMC markets.
- **Government Schemes**: Localized eligibility search for PM-KISAN, Rythu Bandhu, crop insurance, and solar subsidies.
- **Community Pest Alerts**: Crowdsourced village reports with heatmaps to flag early outbreaks.

---

## 🏗️ System Architecture

```
                                  [ Farmer User ]
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
            [ Voice & Web UI ]                       [ WhatsApp Bot ]
         (React + Vite + Speech)                   (Meta Graph API Webhook)
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         ▼
                        ┌─────────────────────────────────┐
                        │     FastAPI Gateway Backend     │
                        │     (Azure Container Apps)      │
                        └────────────────┬────────────────┘
                                         │
             ┌───────────────────────────┼───────────────────────────┐
             ▼                           ▼                           ▼
 ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
 │   Azure AI Services   │   │  Hindsight Memory     │   │   Dual Database Tier  │
 ├───────────────────────┤   ├───────────────────────┤   ├───────────────────────┤
 │ • Azure OpenAI GPT-4o │   │ • Retain (Durable)    │   │ • Amazon DynamoDB     │
 │ • Azure Speech STT/TTS│   │ • Recall (Semantic)   │   │ • MongoDB Atlas       │
 │ • 9 Indian Languages  │   │ • 8-Taxonomy Isolation│   │   (Auto-Fallback)     │
 └───────────────────────┘   └───────────────────────┘   └───────────────────────┘
```

---

## 🌐 Supported Regional Languages

| Language | Native Name | Code | Voice STT / TTS |
|---|---|---|---|
| **English** | English | `en` | Supported |
| **Hindi** | हिन्दी | `hi` | Supported |
| **Telugu** | తెలుగు | `te` | Supported |
| **Tamil** | தமிழ் | `ta` | Supported |
| **Kannada** | ಕನ್ನಡ | `kn` | Supported |
| **Malayalam** | മലയാളം | `ml` | Supported |
| **Bengali** | বাংলা | `bn` | Supported |
| **Gujarati** | ગુજરાતી | `gu` | Supported |
| **Marathi** | मराठी | `mr` | Supported |

---

## 📡 API Reference

### Memory & Learning Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/memory/health` | Health check for Hindsight memory layer |
| `GET` | `/api/memory/summary` | Fetch categorized memories, evolution timeline, and stats |
| `POST` | `/api/memory/retain` | Store a durable farmer constraint or preference |
| `POST` | `/api/memory/recall` | Retrieve semantic memories relevant to a query |
| `DELETE`| `/api/memory/{memory_id}`| Farmer-driven memory deletion |
| `POST` | `/api/recommendations/feedback` | Submit thumbs up/down, harvest outcome, or correction |

### Core Agricultural Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Memory-aware multilingual AI chat |
| `POST` | `/api/voice-chat` | Voice audio input → speech recognition → memory reasoning → audio response |
| `POST` | `/api/crop-recommendation` | Dynamic crop recommendation using NPK, climate, & memory |
| `GET` | `/api/weather` | Hyperlocal weather and farming advisories |
| `GET` | `/api/crop-prices` | Live mandi prices for local APMC markets |
| `POST` | `/api/gov-schemes` | Search and match relevant agricultural subsidies |
| `GET/POST`| `/webhook` | WhatsApp bi-directional webhook |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Azure OpenAI & Azure Speech credentials
- Hindsight Memory API credentials

### 1. Clone & Setup Backend
```bash
git clone https://github.com/lazypandaa/sarthi.git
cd sarthi/backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Azure and Hindsight API keys
```

### 2. Run Backend Server
```bash
uvicorn main:app --reload --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

### 3. Setup & Run Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

### 4. Run Automated Test Suite
```bash
cd ../backend
PYTHONPATH=. .venv/bin/pytest -c pytest.ini tests/ -v
```
To validate end-to-end multi-session memory flow:
```bash
PYTHONPATH=. .venv/bin/python validate_e2e_flow.py
```

---

## 👥 Contributors

Built with pride for **Smart India Hackathon / Hack with HYD 2026**:

| Contributor | GitHub Profile | Role |
|---|---|---|
| **Eshwar Krishna** | [@lazypandaa](https://github.com/lazypandaa) | Full Stack & AI Architecture, Hindsight Memory Engine |
| **Bobby Kagitha** | [@kagithabobby](https://github.com/kagithabobby) | Backend Services, Cloud Infrastructure & Azure Integration |
| **P Eswar** | [@Eeswar-p](https://github.com/Eeswar-p) | Frontend Engineering, Reasoning UI & Data Storytelling |
| **Navya Jonnalagadda** | [@NavyaJonnalagadda015](https://github.com/NavyaJonnalagadda015) | Multilingual Voice Pipelines, Speech Models & Validation |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
