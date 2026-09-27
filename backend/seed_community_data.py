import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from services.azure_table_db import get_azure_table_db

REPORTS_DATA = [
    # --- SEHORE, MADHYA PRADESH (High Activity Hotspot) ---
    {
        "village_id": "Sehore",
        "report_type": "pest",
        "crop": "Soybean",
        "description": "Severe stem fly (Melanagromyza sojae) infestation observed across 6 farms near Ashta road. Seedling stems showing internal tunneling and wilting.",
        "description_english": "Severe stem fly infestation observed across 6 farms near Ashta road. Seedling stems showing internal tunneling and wilting.",
        "severity": "high",
        "language": "hi",
        "days_ago": 1,
        "verified": True,
        "validation_count": 8,
        "validators": ["+919876500001", "+919876500002", "+919876500003"]
    },
    {
        "village_id": "Sehore",
        "report_type": "disease",
        "crop": "Black Gram (Urad)",
        "description": "Yellow Mosaic Virus spreading rapidly in late-sown urad crops. Whitefly vector populations are extremely high due to humid warm weather.",
        "description_english": "Yellow Mosaic Virus spreading rapidly in late-sown urad crops. Whitefly vector populations are extremely high due to humid warm weather.",
        "severity": "high",
        "language": "hi",
        "days_ago": 2,
        "verified": True,
        "validation_count": 6,
        "validators": ["+919876500004", "+919876500005"]
    },
    {
        "village_id": "Sehore",
        "report_type": "pest",
        "crop": "Chickpea (Gram)",
        "description": "Pod borer (Helicoverpa armigera) caterpillars spotted on young gram pods. Pheromone trap counts exceeded 12 moths per trap per night.",
        "description_english": "Pod borer caterpillars spotted on young gram pods. Pheromone trap counts exceeded 12 moths per trap per night.",
        "severity": "high",
        "language": "hi",
        "days_ago": 3,
        "verified": True,
        "validation_count": 5,
        "validators": ["+919876500001", "+919876500006"]
    },
    {
        "village_id": "Sehore",
        "report_type": "pest",
        "crop": "Mustard",
        "description": "Green mustard aphid colonies clustered heavily on flowering twigs. Neem oil 1500ppm spray checked early colonies effectively.",
        "description_english": "Green mustard aphid colonies clustered heavily on flowering twigs. Neem oil 1500ppm spray checked early colonies effectively.",
        "severity": "medium",
        "language": "hi",
        "days_ago": 4,
        "verified": False,
        "validation_count": 2,
        "validators": ["+919876500007"]
    },
    {
        "village_id": "Sehore",
        "report_type": "weather",
        "crop": "Wheat",
        "description": "Unseasonal hail and heavy wind flattened 15 acres of early-sown HD-2967 wheat. Draining excess water immediately helped root aeration.",
        "description_english": "Unseasonal hail and heavy wind flattened 15 acres of early-sown HD-2967 wheat. Draining excess water immediately helped root aeration.",
        "severity": "medium",
        "language": "hi",
        "days_ago": 5,
        "verified": True,
        "validation_count": 9,
        "validators": ["+919876500002", "+919876500008"]
    },
    {
        "village_id": "Sehore",
        "report_type": "success",
        "crop": "Soybean & Pigeon Pea",
        "description": "Intercropping 4 rows of soybean with 2 rows of pigeon pea reduced pod borer damage by 40% and fetched an additional ₹18,000 profit.",
        "description_english": "Intercropping 4 rows of soybean with 2 rows of pigeon pea reduced pod borer damage by 40% and fetched an additional ₹18,000 profit.",
        "severity": "low",
        "language": "hi",
        "days_ago": 6,
        "verified": True,
        "validation_count": 14,
        "validators": ["+919876500003", "+919876500009"]
    },

    # --- GUNTUR, ANDHRA PRADESH (High Activity Hotspot) ---
    {
        "village_id": "Guntur",
        "report_type": "pest",
        "crop": "Chilli",
        "description": "Invasive Black Thrips (Thrips parvispinus) outbreak in Tenali and Mangalagiri mandals. Crinkled leaf margins and heavy floral bud drop.",
        "description_english": "Invasive Black Thrips outbreak in Tenali and Mangalagiri mandals. Crinkled leaf margins and heavy floral bud drop.",
        "severity": "high",
        "language": "te",
        "days_ago": 1,
        "verified": True,
        "validation_count": 12,
        "validators": ["+919876500010", "+919876500011", "+919876500012"]
    },
    {
        "village_id": "Guntur",
        "report_type": "disease",
        "crop": "Chilli",
        "description": "Anthracnose dieback and fruit rot appearing on maturing pods following dense morning dew. Recommended Mancozeb + Carbendazim rotation.",
        "description_english": "Anthracnose dieback and fruit rot appearing on maturing pods following dense morning dew. Recommended Mancozeb + Carbendazim rotation.",
        "severity": "high",
        "language": "te",
        "days_ago": 2,
        "verified": True,
        "validation_count": 7,
        "validators": ["+919876500013", "+919876500014"]
    },
    {
        "village_id": "Guntur",
        "report_type": "pest",
        "crop": "Cotton",
        "description": "Pink bollworm rosetted flowers found in non-Bt border rows. Light traps installed across 20 acres to monitor peak flight periods.",
        "description_english": "Pink bollworm rosetted flowers found in non-Bt border rows. Light traps installed across 20 acres to monitor peak flight periods.",
        "severity": "high",
        "language": "te",
        "days_ago": 3,
        "verified": True,
        "validation_count": 8,
        "validators": ["+919876500010", "+919876500015"]
    },
    {
        "village_id": "Guntur",
        "report_type": "disease",
        "crop": "Cotton",
        "description": "Bacterial blight angular leaf spots progressing onto bolls. Farmers advised to spray Copper Oxychloride 3g/L + Streptocycline 1g/10L.",
        "description_english": "Bacterial blight angular leaf spots progressing onto bolls. Farmers advised to spray Copper Oxychloride + Streptocycline.",
        "severity": "medium",
        "language": "te",
        "days_ago": 4,
        "verified": False,
        "validation_count": 3,
        "validators": ["+919876500016"]
    },
    {
        "village_id": "Guntur",
        "report_type": "success",
        "crop": "Chilli",
        "description": "Installing 40 yellow and blue sticky cards per acre reduced chemical pesticide applications from 9 to 4 sprays, saving ₹6,000 per acre.",
        "description_english": "Installing 40 yellow and blue sticky cards per acre reduced chemical pesticide applications from 9 to 4 sprays, saving ₹6,000 per acre.",
        "severity": "low",
        "language": "te",
        "days_ago": 5,
        "verified": True,
        "validation_count": 18,
        "validators": ["+919876500017", "+919876500018"]
    },

    # --- NASHIK, MAHARASHTRA (Active Hotspot) ---
    {
        "village_id": "Nashik",
        "report_type": "disease",
        "crop": "Onion",
        "description": "Purple blotch (Alternaria porri) flare-up in Niphad taluka after cloudy days. Elliptical purple lesions with yellow halos on older leaves.",
        "description_english": "Purple blotch flare-up in Niphad taluka after cloudy days. Elliptical purple lesions with yellow halos on older leaves.",
        "severity": "high",
        "language": "mr",
        "days_ago": 2,
        "verified": True,
        "validation_count": 11,
        "validators": ["+919876500020", "+919876500021"]
    },
    {
        "village_id": "Nashik",
        "report_type": "pest",
        "crop": "Onion",
        "description": "Onion thrips causing silvery sheen on central leaves and bulb stunting. Neem extract + Spinetoram spray gave 85% knockdown.",
        "description_english": "Onion thrips causing silvery sheen on central leaves and bulb stunting. Neem extract + Spinetoram spray gave 85% knockdown.",
        "severity": "medium",
        "language": "mr",
        "days_ago": 3,
        "verified": True,
        "validation_count": 6,
        "validators": ["+919876500022"]
    },
    {
        "village_id": "Nashik",
        "report_type": "disease",
        "crop": "Grape",
        "description": "Downy mildew oil spots observed on young grape shoots in Dindori. Humidity above 90% creating high infection risk for berry clusters.",
        "description_english": "Downy mildew oil spots observed on young grape shoots in Dindori. Humidity above 90% creating high infection risk for berry clusters.",
        "severity": "high",
        "language": "mr",
        "days_ago": 4,
        "verified": True,
        "validation_count": 9,
        "validators": ["+919876500023", "+919876500024"]
    },
    {
        "village_id": "Nashik",
        "report_type": "success",
        "crop": "Pomegranate",
        "description": "Bagging individual pomegranate fruits with perforated non-woven bags eliminated fruit borer damage completely without insecticides.",
        "description_english": "Bagging individual pomegranate fruits with perforated non-woven bags eliminated fruit borer damage completely without insecticides.",
        "severity": "low",
        "language": "mr",
        "days_ago": 6,
        "verified": True,
        "validation_count": 15,
        "validators": ["+919876500025"]
    },

    # --- WARANGAL, TELANGANA ---
    {
        "village_id": "Warangal",
        "report_type": "pest",
        "crop": "Maize",
        "description": "Fall Armyworm (Spodoptera frugiperda) detected in whorl stage maize around Parkal. Heavy leaf raggedness and sawdust frass present.",
        "description_english": "Fall Armyworm detected in whorl stage maize around Parkal. Heavy leaf raggedness and sawdust frass present.",
        "severity": "high",
        "language": "te",
        "days_ago": 2,
        "verified": True,
        "validation_count": 10,
        "validators": ["+919876500030", "+919876500031"]
    },
    {
        "village_id": "Warangal",
        "report_type": "disease",
        "crop": "Paddy (Rice)",
        "description": "Sheath blight (Rhizoctonia solani) lesions forming green-gray oval patterns near water level. Farmers advised to drain water for 3 days.",
        "description_english": "Sheath blight lesions forming green-gray oval patterns near water level. Farmers advised to drain water for 3 days.",
        "severity": "medium",
        "language": "te",
        "days_ago": 3,
        "verified": False,
        "validation_count": 3,
        "validators": ["+919876500032"]
    },
    {
        "village_id": "Warangal",
        "report_type": "pest",
        "crop": "Paddy (Rice)",
        "description": "Brown Planthopper (BPH) early circular hopperburn patches spotted in dense tillered fields. Avoid synthetic pyrethroids to prevent flare-up.",
        "description_english": "Brown Planthopper early circular hopperburn patches spotted in dense tillered fields. Avoid synthetic pyrethroids.",
        "severity": "high",
        "language": "te",
        "days_ago": 5,
        "verified": True,
        "validation_count": 7,
        "validators": ["+919876500033"]
    },
    {
        "village_id": "Warangal",
        "report_type": "success",
        "crop": "Paddy (Rice)",
        "description": "Direct Seeded Rice (DSR) using drum seeder cut labor cost by 60% and matured 10 days earlier with zero yield penalty.",
        "description_english": "Direct Seeded Rice using drum seeder cut labor cost by 60% and matured 10 days earlier with zero yield penalty.",
        "severity": "low",
        "language": "te",
        "days_ago": 6,
        "verified": True,
        "validation_count": 21,
        "validators": ["+919876500034", "+919876500035"]
    },

    # --- KARNAL, HARYANA ---
    {
        "village_id": "Karnal",
        "report_type": "disease",
        "crop": "Wheat",
        "description": "Yellow rust (Puccinia striiformis) bright yellow uredinial pustules in linear rows on flag leaves. Immediate spray of Propiconazole 0.1% carried out.",
        "description_english": "Yellow rust bright yellow pustules in linear rows on flag leaves. Immediate spray of Propiconazole 0.1% carried out.",
        "severity": "high",
        "language": "hi",
        "days_ago": 1,
        "verified": True,
        "validation_count": 14,
        "validators": ["+919876500040", "+919876500041"]
    },
    {
        "village_id": "Karnal",
        "report_type": "weather",
        "crop": "Wheat & Mustard",
        "description": "Heavy fog and morning frost duration exceeding 4 hours. Light night irrigation advised to buffer canopy temperature against cold injury.",
        "description_english": "Heavy fog and morning frost duration exceeding 4 hours. Light night irrigation advised to buffer canopy temperature.",
        "severity": "medium",
        "language": "hi",
        "days_ago": 3,
        "verified": True,
        "validation_count": 8,
        "validators": ["+919876500042"]
    },
    {
        "village_id": "Karnal",
        "report_type": "success",
        "crop": "Wheat",
        "description": "Zero-tillage Happy Seeder wheat planting directly into standing paddy straw saved ₹3,200/acre in land prep and preserved soil moisture.",
        "description_english": "Zero-tillage Happy Seeder wheat planting directly into standing paddy straw saved ₹3,200/acre in land prep and preserved soil moisture.",
        "severity": "low",
        "language": "hi",
        "days_ago": 5,
        "verified": True,
        "validation_count": 19,
        "validators": ["+919876500043"]
    },

    # --- COIMBATORE, TAMIL NADU ---
    {
        "village_id": "Coimbatore",
        "report_type": "pest",
        "crop": "Coconut",
        "description": "Rugose Spiralling Whitefly (Aleurodicus rugioperculatus) wax deposits under fronds. Release of Encarsia guadeloupae biocontrol showed 70% parasitism.",
        "description_english": "Rugose Spiralling Whitefly wax deposits under fronds. Release of Encarsia parasitoid biocontrol showed 70% parasitism.",
        "severity": "medium",
        "language": "ta",
        "days_ago": 2,
        "verified": True,
        "validation_count": 9,
        "validators": ["+919876500050", "+919876500051"]
    },
    {
        "village_id": "Coimbatore",
        "report_type": "disease",
        "crop": "Banana",
        "description": "Panama wilt (Fusarium oxysporum) vascular yellowing in G9 cultivar. Root dipping with Pseudomonas fluorescens 10g/L contained patch spread.",
        "description_english": "Panama wilt vascular yellowing in G9 cultivar. Root treatment with Pseudomonas fluorescens contained patch spread.",
        "severity": "high",
        "language": "ta",
        "days_ago": 4,
        "verified": True,
        "validation_count": 6,
        "validators": ["+919876500052"]
    },
    {
        "village_id": "Coimbatore",
        "report_type": "success",
        "crop": "Coconut Multi-Tier",
        "description": "Multi-tier farming of nutmeg and black pepper under coconut canopy generated ₹2.4 Lakhs net income per acre with solar drip automation.",
        "description_english": "Multi-tier farming of nutmeg and black pepper under coconut canopy generated ₹2.4 Lakhs net income per acre with solar drip automation.",
        "severity": "low",
        "language": "ta",
        "days_ago": 6,
        "verified": True,
        "validation_count": 27,
        "validators": ["+919876500053", "+919876500054"]
    }
]

VILLAGE_TRUST_DATA = [
    {"village_id": "Sehore", "total": 142, "helpful": 131, "trust_score": 92.25},
    {"village_id": "Guntur", "total": 198, "helpful": 182, "trust_score": 91.92},
    {"village_id": "Nashik", "total": 165, "helpful": 154, "trust_score": 93.33},
    {"village_id": "Warangal", "total": 110, "helpful": 97, "trust_score": 88.18},
    {"village_id": "Karnal", "total": 125, "helpful": 119, "trust_score": 95.20},
    {"village_id": "Coimbatore", "total": 150, "helpful": 141, "trust_score": 94.00},
    {"village_id": "India", "total": 850, "helpful": 782, "trust_score": 92.00}
]

def seed_community():
    db = get_azure_table_db()
    reports_table = db.Table('sarthicommunityreports')
    trust_table = db.Table('sarthivillagetrust')

    print("🚀 Seeding realistic agricultural community reports...")
    now = datetime.utcnow()

    seeded_reports = 0
    for item in REPORTS_DATA:
        ts = (now - timedelta(days=item["days_ago"], hours=seeded_reports * 2)).isoformat()
        report_id = f"cr_{item['village_id'].lower()}_{seeded_reports + 1:03d}"
        
        record = {
            "report_id": report_id,
            "user_phone": item["validators"][0] if item["validators"] else "+919999999001",
            "village_id": item["village_id"],
            "report_type": item["report_type"],
            "crop": item["crop"],
            "description": item["description"],
            "description_english": item["description_english"],
            "severity": item["severity"],
            "language": item["language"],
            "timestamp": ts,
            "verified": item["verified"],
            "validation_count": item["validation_count"],
            "validators": item["validators"]
        }
        reports_table.put_item(Item=record)
        seeded_reports += 1

    print(f"✅ Successfully seeded {seeded_reports} community reports!")

    print("🚀 Seeding village trust scores...")
    for vt in VILLAGE_TRUST_DATA:
        trust_table.put_item(Item={
            "village_id": vt["village_id"],
            "total_responses": vt["total"],
            "helpful_count": vt["helpful"],
            "trust_score": vt["trust_score"],
            "last_updated": now.isoformat()
        })
    print(f"✅ Successfully seeded {len(VILLAGE_TRUST_DATA)} village trust records!")

if __name__ == "__main__":
    seed_community()
