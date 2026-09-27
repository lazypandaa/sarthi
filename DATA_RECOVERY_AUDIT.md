# DATA RECOVERY AUDIT: GRAM VAANI AGRICULTURAL AI PLATFORM
**Date:** September 2026  
**Auditor:** Antigravity Advanced Agentic AI  
**Scope:** Complete repository audit across frontend, backend, database models, external APIs, and agricultural datasets.

---

## 1. Executive Summary
Gram Vaani is an AI-powered agricultural intelligence application designed for Indian farmers. The application previously had a comprehensive vision for hyper-local agricultural data (soil, climate, crops, calendar, mandi prices, official advisories, pest/disease outbreaks). 

During previous development phases, when the application was migrated from MongoDB/AWS to Azure Table Storage + Azure OpenAI + Hindsight Cloud, the agricultural data layer was partially left behind:
1. Core application entities (`users`, `queries`, `sessions`, `community_reports`, `village_trust`) were successfully wired to Azure Table Storage (`services/azure_table_db.py`).
2. Crucial agricultural reference services (`hyperlocal_context`, `environmental_profiles`, `crop_recommendations`, `optimization_strategies`, `agriculture_news`, `pest_reports`, `disease_reports`) remained tied to an unreachable `MongoClient(os.getenv("MONGO_URL"))`.
3. Frontend components (`Advisor.jsx`, `CropCalendar.jsx`, `Profile.jsx`) hardcoded `http://localhost:8000`, causing network failure in cloud environments (Azure Static Web Apps).
4. Crop calendar relied on a basic 9-crop static JSON file and attempted to call AWS Translate (`boto3`) rather than a localized/cached schema.
5. Weather and Mandi market data were either fetched per request without local caching or returned hardcoded dictionaries.

This audit details what works, what is broken, what data exists locally in the repository, and the precise recovery roadmap.

---

## 2. Component-by-Component Status Matrix

| Component / Feature | Current Implementation Status | Root Cause / Issue | Recovery Action |
| :--- | :--- | :--- | :--- |
| **Authentication & Profile** | ✅ Working (Azure Table Storage) | Phone auth, JWT, profile edit works. | Connect profile to regional soil and district data. |
| **Hindsight Memory Integration** | ✅ Working (Hindsight Cloud) | 39 automated tests pass. Real Retain/Recall operational. | Preserve strictly; feed localized agricultural reference data alongside memories. |
| **Community Reports & Outbreaks** | ✅ Working (Azure Table Storage) | 25 Indian reports across 6 regions + 5 active clusters seeded. | Connect to district-level pest/disease alerts. |
| **Hyperlocal Context (Soil & District)** | ❌ Disconnected | `data_aggregator.py` tries to query `db.hyperlocal_context` in MongoDB, times out. | Migrate to local SQLite/Azure Table cache using `all_india_districts.py` and `andhra_pradesh_complete.py`. |
| **Crop Recommendations (Advisor)** | ❌ Broken (500 Error) | `/api/crop-recommendations` queries `mongo_db.crop_recommendations` which is unreachable. | Build database-backed recommendation engine with soil/season/water compatibility. |
| **Farming Optimization Strategies** | ❌ Broken / Fallback | `/api/optimization-strategies` queries `mongo_db` and falls back to empty. | Store normalized agronomic strategies locally in DB/cache. |
| **Agricultural Advisories & News** | ⚠️ Stale / Fallback | `/api/agriculture-news` tries Mongo then serves static sample array. | Build synchronized advisory service with official ICAR/IMD Agromet data. |
| **Crop Calendar** | ⚠️ Limited / Partially Broken | Reads static 9-crop `crop_calendar.json`; fails on non-English because of legacy AWS Translate call. | Create normalized, multi-season, 50+ Indian crop calendar with local translations and state filtering. |
| **Weather Information** | ⚠️ Uncached / External Dependency | Direct request to OpenWeather per call; fallback 25°C. | Add local database caching (1-hour TTL) with coordinates mapping and IMD Agromet format. |
| **Market / Mandi Data** | ⚠️ Hardcoded / Mocked | `get_crop_prices` returns hardcoded static dictionary (`wheat: 2000...`). | Connect to official Agmarknet/e-NAM normalized dataset with daily/periodic sync. |
| **Mobile Responsiveness** | ⚠️ Partial | Desktop layout tables, fixed containers, no mobile hamburger menu. | Implement fluid CSS Grid/Flexbox, responsive calendar cards, and mobile bottom navigation. |

---

## 3. Discovered Local Agricultural Datasets

The repository already contains high-value agricultural datasets that were orphaned during database migrations:

1. **`all_india_districts.py` (15.4 KB)**:
   - Contains all **700+ districts across all 28 states and 8 Union Territories**.
   - Contains state-wise agricultural profiles: soil types (Alluvial, Black, Red Sandy Loam, Laterite, Mountain), annual rainfall ranges, and typical seasonal crops (Kharif, Rabi, Summer).
2. **`andhra_pradesh_complete.py` (4.6 KB)**:
   - Comprehensive agricultural data for all **26 districts of Andhra Pradesh** (post-2022 reorganization including Bapatla, Palnadu, Konaseema, NTR, Tirupati, etc.).
   - Includes specific soil classifications, average rainfall, and major crops per season.
3. **`india_complete_data.py` (13.8 KB)**:
   - Multi-district agricultural profiles for Karnataka, Maharashtra, Punjab, Haryana, Tamil Nadu, Madhya Pradesh, West Bengal, Bihar, and Uttar Pradesh.
4. **`hyperlocal_data.py` (3.4 KB)**:
   - Regional soil parameters, seasonal calendar associations, and local farmer success stories.
5. **`crop_calendar.json` (3.6 KB)**:
   - Baseline schema for sowing windows, harvesting windows, duration, and agronomic management tips.
6. **`govt_api_integration.py` (10.8 KB)**:
   - Working Agmarknet API integration via `api.data.gov.in` (Resource ID: `9ef84268-d588-465a-a308-a864a43d0070`).
   - ICAR pest surveillance taxonomy (Fall Armyworm, Pink Bollworm, Brown Plant Hopper, Aphids, Fruit Fly).
   - ICAR disease surveillance taxonomy (Blast, Late Blight, Yellow Mosaic Virus, Powdery Mildew, Wilt).

---

## 4. Discovered Backend & Frontend Architecture Gaps

### A. Backend Gaps
1. **Dual Database Conflict**:
   - `services/azure_table_db.py` provides SQLite fallback (`data/sarthi_local.db`) and Azure Table Storage (`sarthistore`).
   - `main.py` and `data_aggregator.py` import `MongoClient` and attempt to call `mongo_db.hyperlocal_context`, `mongo_db.crop_recommendations`, etc.
   - Solution: Unify all agricultural reference data into the `AzureTableWrapper` / SQLite local database cache (`sarthicropmaster`, `sarthicropcalendar`, `sarthisoilreference`, `sarthiadvisories`, `sarthimarketprices`).
2. **AWS Translate Zombie Code**:
   - In `/api/crop-calendar`, lines 1285-1355 attempt to call `translate_client.translate_text` (`boto3`). In Azure or local environments without AWS credentials, this throws exceptions.
   - Solution: Use built-in multilingual dictionaries from `frontend/src/translations.js` or Azure OpenAI translation.
3. **Uncached Weather & Market Calls**:
   - Every weather request hit external HTTP. If the API key is rate-limited or fails, a generic 25°C clear response is returned.

### B. Frontend Gaps
1. **Hardcoded URLs**:
   - `frontend/src/Advisor.jsx`: Lines 52, 65, 77, 115 call `http://localhost:8000`.
   - `frontend/src/CropCalendar.jsx`: Line 190 calls `http://localhost:8000`.
   - `frontend/src/Profile.jsx` & `ProfileNew.jsx`: Lines 28, 35, 55, 62 call `http://localhost:8000`.
   - Solution: Import and use `API_URL` from `./config`.
2. **Mobile Layout**:
   - `CropCalendar.jsx` renders desktop table cells without mobile card transformation.
   - `Navbar.jsx` has 7 desktop tabs that wrap or overflow horizontally on screens < 768px.

---

## 5. Architectural Blueprint for Restoration

```
┌─────────────────────────────────────────────────────────────┐
│             OFFICIAL AGRICULTURAL SOURCES (ETL)             │
│   • Agmarknet / e-NAM (Mandis)  • IMD (Agromet Weather)     │
│   • ICAR / Agrisnet (Advisories)• Soil Health Card Datasets │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Idempotent Ingestion / CLI)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│          NORMALIZED LOCAL DATABASE & PERSISTENCE            │
│   • Azure Table Storage (`sarthistore`)                     │
│   • Local SQLite Database (`backend/data/sarthi_local.db`)  │
│   ───────────────────────────────────────────────────────   │
│   Tables:                                                   │
│   1. sarthilocations       (700+ Indian districts & hierarchy)│
│   2. sarthisoilreference   (Soil types, pH, NPK, textures)   │
│   3. sarthicropmaster      (Comprehensive agronomic profiles)│
│   4. sarthicropcalendar    (Sowing/Harvesting windows)       │
│   5. sarthiadvisories      (ICAR/IMD Agromet bulletins)      │
│   6. sarthimarketprices    (Daily mandi arrivals & prices)   │
│   7. sarthicommunityreports(Field observations & outbreaks)  │
│   8. sarthiweathercache    (Cached observations & warnings)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Fast local queries (<10ms)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FAST BACKEND APIS                      │
│   • GET /api/location/*        • GET /api/soil/*            │
│   • GET /api/crop-calendar     • GET /api/crop-recommendations│
│   • GET /api/weather           • GET /api/agriculture-news  │
│   • GET /api/markets           • POST /api/recommendation   │
│   (Combined with real-time Hindsight memory recall)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON via HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSIVE FRONTEND                      │
│   • Fluid Breakpoints (320px – 1440px)                      │
│   • Mobile Navigation Drawer / Bottom Navigation            │
│   • Touch-friendly Crop Calendar Cards                      │
│   • Outbreak Map & Village Reports                          │
│   • Personalized Chat & Advisory                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Execution Roadmap
1. **Phase 1**: Audit + Data Source Documentation (`DATA_RECOVERY_AUDIT.md`, `DATA_SOURCES.md`).
2. **Phase 2**: Database/Data-Model restoration (create normalized Azure Table / SQLite models).
3. **Phase 3**: Bulk data ingestion (seed all 700+ districts, 50+ crops, calendar, soil, advisories, mandi prices).
4. **Phase 4**: Backend APIs restoration (decouple from MongoDB, fix endpoints).
5. **Phase 5**: Recommendation engine restoration (soil + weather + season + Hindsight memory).
6. **Phase 6**: Advisory + Weather + Soil + Market APIs.
7. **Phase 7**: Crop Calendar restoration.
8. **Phase 8**: Community + Outbreak Map integration.
9. **Phase 9**: Hindsight memory integration verification.
10. **Phase 10**: Responsive mobile implementation.
11. **Phase 11**: End-to-end testing.
12. **Phase 12**: Performance validation and UI polish.
