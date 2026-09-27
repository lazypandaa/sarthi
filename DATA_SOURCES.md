# DATA SOURCES DIRECTORY: AUTHORITATIVE AGRICULTURAL DATASETS
**Project:** Gram Vaani (Sarthi) Agricultural AI Platform  
**Compliance Standard:** Government of India Open Data Policy (NDSAP) & Authoritative Agricultural Research  
**Last Verified:** September 2026

---

## 1. Directory of Official Agricultural Sources

### 1. Agmarknet (Agricultural Marketing Information Network)
- **Organization:** Directorate of Marketing & Inspection (DMI), Ministry of Agriculture & Farmers Welfare, Government of India.
- **Official URL:** [agmarknet.gov.in](https://agmarknet.gov.in) / [api.data.gov.in](https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070)
- **Type:** REST API & daily downloadable bulletin.
- **Authentication:** `api-key` required via `data.gov.in` (pre-configured in `backend/govt_api_integration.py`).
- **Update Frequency:** Daily (updated as APMC mandis report daily arrivals).
- **Geographic Coverage:** Pan-India (over 3,200 regulated APMC markets across all states).
- **Temporal Coverage:** Historical from 2002 to present; real-time daily transactions.
- **Key Variables:** `state`, `district`, `market` (mandi name), `commodity`, `variety`, `arrival_date`, `min_price`, `max_price`, `modal_price` (in ₹/quintal).
- **Format:** JSON / CSV.
- **License / Access:** Open Government Data (OGD) License India. Free to use with attribution.
- **Caching / Storage Permitted:** Yes. Highly recommended to cache locally to avoid excessive load on public API endpoints.
- **Ingestion Automation:** Automated via periodic ETL job (`sync_markets`).
- **Intended Feature:** Market / Mandi Price Intelligence on Dashboard, Advisor, and personalized crop sale recommendations.

---

### 2. India Meteorological Department (IMD) & Agromet Advisory Services (AAS)
- **Organization:** Ministry of Earth Sciences (MoES), Government of India.
- **Official URL:** [mausam.imd.gov.in](https://mausam.imd.gov.in) & [agromet.imd.gov.in](https://agromet.imd.gov.in)
- **Type:** District Agromet Bulletins (Gramin Krishi Mausam Sewa - GKMS) & Official Weather Forecast API.
- **Authentication:** Public bulletins / API token where registered; OpenWeather / OGD APIs for high-throughput localized coordinate weather.
- **Update Frequency:** Bi-weekly bulletins (Tuesdays & Fridays) for Agromet advisories; 3-hourly / daily for weather observations and 5-day forecasts.
- **Geographic Coverage:** Pan-India down to district and block (Panchayat level through GKMS).
- **Temporal Coverage:** Past 7 days observations, 5-day forecasts, seasonal monsoon projections.
- **Key Variables:** `temperature_max`, `temperature_min`, `relative_humidity`, `rainfall_mm`, `wind_speed_kmph`, `wind_direction`, `cloud_cover`, `extreme_weather_alerts`, `crop_specific_weather_advisories`.
- **Format:** JSON, XML, PDF bulletins.
- **License / Access:** Public domain for Indian agriculture and disaster risk reduction.
- **Caching / Storage Permitted:** Yes. IMD guidelines explicitly recommend client-side and application-level caching.
- **Ingestion Automation:** Periodic sync (hourly weather cache TTL, bi-weekly advisory sync).
- **Intended Feature:** Live Weather Widget, Sowing/Harvesting Alerts, Spraying Conditions Advisor, Hail/Frost warnings.

---

### 3. Soil Health Card (SHC) Portal & ICAR-NBSS&LUP
- **Organization:** Department of Agriculture & Farmers Welfare, GoI + ICAR-National Bureau of Soil Survey and Land Use Planning.
- **Official URL:** [soilhealth.dac.gov.in](https://soilhealth.dac.gov.in) & [nbsslup.icar.gov.in](https://nbsslup.icar.gov.in)
- **Type:** National Soil Database, District Soil Maps, and Soil Fertility Atlases.
- **Authentication:** Public state/district aggregates; farmer credentials required for individual card retrieval.
- **Update Frequency:** Cycle-based (Cycles I, II, and ongoing Soil Health Management campaigns).
- **Geographic Coverage:** All 700+ Indian districts and agro-ecological zones.
- **Temporal Coverage:** Baseline fertility norms and annual cycle summaries.
- **Key Variables:** 12 Core Soil Parameters:
  - Macronutrients: Nitrogen (N), Phosphorus (P), Potassium (K)
  - Secondary: Sulphur (S)
  - Micronutrients: Zinc (Zn), Iron (Fe), Copper (Cu), Manganese (Mn), Boron (B)
  - Physical: pH (acidity/alkalinity), Electrical Conductivity (EC - salinity), Organic Carbon (OC - organic matter percentage).
- **Format:** Normalized JSON reference schemas, Geospatial GeoJSON, CSV.
- **License / Access:** Government public data.
- **Caching / Storage Permitted:** Yes. Reference regional baseline data should be permanently cached in local DB.
- **Ingestion Automation:** Idempotent seed script (`sync_soil`).
- **Intended Feature:** District-level Soil Intelligence, Fertilizer Dosing Advisor, and Soil-Crop Compatibility Filtering.

---

### 4. ICAR (Indian Council of Agricultural Research) & Crop Knowledge Repository
- **Organization:** Indian Council of Agricultural Research, Department of Agricultural Research and Education (DARE).
- **Official URL:** [icar.org.in](https://icar.org.in) / Specialized Institutes (CRRI, IARI, IIOR, IIMR, NBAIR).
- **Type:** Crop Production Handbooks, Package of Practices, Pest & Disease Identification Keys.
- **Authentication:** Open access publications.
- **Update Frequency:** Seasonal and annual variety releases.
- **Geographic Coverage:** All 15 Agro-Climatic Zones of India.
- **Temporal Coverage:** Kharif, Rabi, and Zaid/Summer seasons.
- **Key Variables:** `crop_id`, `crop_name`, `scientific_name`, `varieties`, `sowing_window`, `harvesting_window`, `duration_days`, `water_requirement_mm`, `temperature_tolerance`, `pest_susceptibility`, `integrated_pest_management_steps`.
- **Format:** Structured agronomic records.
- **License / Access:** Academic / Public agricultural extension.
- **Caching / Storage Permitted:** Yes.
- **Ingestion Automation:** Seeded into master crop table (`sarthicropmaster` & `sarthicropcalendar`).
- **Intended Feature:** Crop Calendar, Crop Suitability Engine, Diagnostic AI System.

---

### 5. Open Government Data (OGD) Platform India (data.gov.in)
- **Organization:** National Informatics Centre (NIC), Ministry of Electronics & IT, Government of India.
- **Official URL:** [data.gov.in](https://data.gov.in)
- **Type:** Central Open Data Catalog (REST APIs + CSV/JSON).
- **Authentication:** `api-key` header/parameter.
- **Update Frequency:** Monthly to annual depending on catalog catalog.
- **Geographic Coverage:** National, State, and District levels.
- **Key Datasets Utilized:**
  1. *District-wise, season-wise crop production statistics (DES)*
  2. *Daily wholesale market prices for agriculture commodities*
  3. *Rainfall statistics by meteorological sub-division*
- **License / Access:** Government Open Data License - India (GODL).
- **Caching / Storage Permitted:** Yes.
- **Ingestion Automation:** Automated scheduled ETL.
- **Intended Feature:** Historical yield benchmarks, regional crop prevalence scoring.

---

### 6. State Agriculture Departments (Special Focus: Andhra Pradesh & MP)
- **Organization:** 
  - Department of Agriculture, Government of Andhra Pradesh ([apagrisnet.gov.in](https://apagrisnet.gov.in))
  - Department of Farmer Welfare and Agriculture Development, MP ([mpkrishi.mp.gov.in](https://mpkrishi.mp.gov.in))
- **Type:** State Package of Practices, Rythu Bharosa / Mandi port bulletins, District Agriculture Action Plans.
- **Authentication:** Public portals.
- **Update Frequency:** Seasonal.
- **Geographic Coverage:** Complete 26 districts of Andhra Pradesh + 52 districts of Madhya Pradesh.
- **Key Variables:** Mandal-level recommended varieties, district rainfall targets, localized pest advisories (e.g. *Thrips parvispinus* in AP Chillies, Stem fly in MP Soybeans).
- **License / Access:** Public agricultural advisories.
- **Caching / Storage Permitted:** Yes.
- **Ingestion Automation:** Seeded directly into `sarthilocations`, `sarthisoilreference`, and `sarthiadvisories`.
- **Intended Feature:** Hyper-local relevance for primary user base.

---

## 2. Ingestion & Storage Architecture Matrix

| Dataset Category | Primary Authoritative Source | Local Table / Storage | Freshness / Sync Policy | Ingestion Script |
| :--- | :--- | :--- | :--- | :--- |
| **Locations** | Census of India / GoI Local Government Directory (LGD) | `sarthilocations` (Azure Table / SQLite) | Static (re-seed on structural changes) | `ingestion/sync_locations.py` |
| **Soil Reference** | Soil Health Card / ICAR-NBSS&LUP | `sarthisoilreference` | Semi-static (annual review) | `ingestion/sync_soil.py` |
| **Crop Master** | ICAR Package of Practices | `sarthicropmaster` | Semi-static | `ingestion/sync_crops.py` |
| **Crop Calendar** | State Agrisnet / ICAR Agro-Climatic Guides | `sarthicropcalendar` | Seasonal | `ingestion/sync_crop_calendar.py` |
| **Advisories** | IMD GKMS Agromet / State Ag Depts | `sarthiadvisories` | Weekly (7-day TTL) | `ingestion/sync_advisories.py` |
| **Market Prices** | Agmarknet (data.gov.in) | `sarthimarketprices` | Daily (24-hour TTL) | `ingestion/sync_markets.py` |
| **Weather** | IMD / Local Cache | `sarthiweathercache` | 1-hour cache TTL | Integrated Backend Service |
| **Community / Outbreaks**| Peer Verified Field Sightings | `sarthicommunityreports` | Real-time write, immediate cluster aggregation | Integrated API |

---

## 3. Strict Data Integrity Governance
1. **Provenance Enforcement**: Every record in the database includes `source`, `source_url`, `fetched_at`, and `verified` flags.
2. **No Data Fabrication**: If an external API is momentarily unreachable, the system serves valid cached data with a clear "cached from [timestamp]" indicator. If no cached data exists, an honest empty state is returned.
3. **Strict Separation of Memory vs Reference Data**:
   - Hindsight Cloud stores only subjective farmer experiences, personal constraints, and conversational learnings.
   - Authoritative agronomic facts, soil norms, and official market prices are strictly stored in the database layer.
