from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from openai import AzureOpenAI
import os
import base64
# Azure Speech SDK is optional - only import if available
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False
    print("Azure Speech SDK not available - using AWS Polly for all languages")
import boto3
from dotenv import load_dotenv
import requests
import jwt
from datetime import datetime, timedelta
from typing import Optional
from transcribe_service import TranscribeService
import bcrypt
import uuid
import asyncio
from pymongo import MongoClient
from data_aggregator import fetch_all_context_data, format_context_for_llm, fetch_context_sync
from services.hindsight import (
    get_memory_service,
    get_recommender,
    MemoryType,
    MemorySource,
)
from services.azure_table_db import get_azure_table_db

load_dotenv()

# Amazon Translate client (optional fallback)
try:
    translate_client = boto3.client('translate', region_name='ap-south-1')
except Exception:
    translate_client = None

# MongoDB connection for hyperlocal data (with connection pooling)
mongo_client = MongoClient(
    os.getenv("MONGO_URL"),
    maxPoolSize=10,  # Connection pool
    minPoolSize=2,
    maxIdleTimeMS=30000,  # 30 seconds
    serverSelectionTimeoutMS=5000  # 5 seconds timeout
)
mongo_db = mongo_client.gramvani
hyperlocal_collection = mongo_db.hyperlocal_context
success_stories_collection = mongo_db.success_stories
pest_outbreaks_collection = mongo_db.pest_outbreaks

app = FastAPI()

# Azure Table Storage connection (Replaces AWS DynamoDB)
azure_db = get_azure_table_db()
users_table = azure_db.Table('sarthiusers')
queries_table = azure_db.Table('sarthiqueries')
sessions_table = azure_db.Table('sarthisessions')
village_trust_table = azure_db.Table('sarthivillagetrust')
community_reports_table = azure_db.Table('sarthicommunityreports')

print("Azure Table Storage initialized (sarthistore)")

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://lazypandaa.github.io",
    "https://eshwarkrishna.me",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI
azure_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
)

# Amazon Polly
polly_client = boto3.client("polly", region_name="ap-south-1")

# Amazon Transcribe (optional - requires AWS_S3_BUCKET)
try:
    transcribe_service = TranscribeService()
except Exception as e:
    transcribe_service = None
    print(f"TranscribeService not available: {e}")

# WhatsApp credentials
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

LANGUAGE_TO_LOCALE = {
    "en": "en-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "bn": "bn-IN",
    "gu": "gu-IN",
    "mr": "mr-IN",
}

# AWS Polly voices for all Indian languages
LANGUAGE_TO_POLLY_VOICE = {
    "en": ("Joanna", "en-US"),
    "hi": ("Aditi", "hi-IN"),
    # Fallback to Hindi voice for other Indian languages if Azure Speech not available
    "ta": ("Aditi", "hi-IN"),
    "te": ("Aditi", "hi-IN"),
    "kn": ("Aditi", "hi-IN"),
    "ml": ("Aditi", "hi-IN"),
    "bn": ("Aditi", "hi-IN"),
    "gu": ("Aditi", "hi-IN"),
    "mr": ("Aditi", "hi-IN"),
}

# Azure Speech for other Indian languages (only if SDK is available)
AZURE_SPEECH_VOICES = {
    "ta": "ta-IN-ValluvarNeural",
    "te": "te-IN-ShrutiNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "bn": "bn-IN-BashkarNeural",
    "gu": "gu-IN-DhwaniNeural",
    "mr": "mr-IN-AarohiNeural",
}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "bn": "Bengali",
    "gu": "Gujarati",
    "mr": "Marathi",
}

def translate_to_english(text: str, source_lang: str) -> str:
    """Translate text to English using Azure OpenAI GPT"""
    if source_lang == "en":
        return text
    try:
        language_name = LANGUAGE_NAMES.get(source_lang, "Unknown")
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following {language_name} text to English. Only return the translated text, nothing else."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def synthesize_speech(text: str, language: str) -> Optional[str]:
    if not text:
        return None
    
    # Try Azure Speech for regional languages if available and configured
    if AZURE_SPEECH_AVAILABLE and language in AZURE_SPEECH_VOICES:
        try:
            speech_key = os.getenv("AZURE_SPEECH_KEY")
            speech_region = os.getenv("AZURE_SPEECH_REGION")
            
            if speech_key and speech_region:
                speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
                voice_name = AZURE_SPEECH_VOICES.get(language)
                speech_config.speech_synthesis_voice_name = voice_name
                speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
                
                print(f"Azure Speech TTS: voice={voice_name}, region={speech_region}")
                
                synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
                result = synthesizer.speak_text_async(text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return base64.b64encode(result.audio_data).decode("utf-8")
                else:
                    print(f"Azure Speech synthesis failed: {result.reason}, falling back to Polly")
        except Exception as e:
            print(f"Azure Speech synthesis error: {e}, falling back to Polly")
    
    # Use AWS Polly as default/fallback for all languages
    try:
        voice_config = LANGUAGE_TO_POLLY_VOICE.get(language, ("Joanna", "en-US"))
        voice_id, language_code = voice_config
        
        print(f"Polly TTS: voice={voice_id}, language={language_code}")
        
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            LanguageCode=language_code
        )
        audio_data = response["AudioStream"].read()
        return base64.b64encode(audio_data).decode("utf-8")
    except Exception as e:
        print(f"Polly synthesis error: {e}")
        return None

# Models
class UserSignup(BaseModel):
    phone_number: str
    password: str
    language: str
    location: str

class UserLogin(BaseModel):
    phone_number: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TextRequest(BaseModel):
    text: str
    language: str = "en"

class WeatherRequest(BaseModel):
    city: Optional[str] = None
    language: str = "en"

class CropPriceRequest(BaseModel):
    crop: str
    market: Optional[str] = None
    language: str = "en"

class SchemeRequest(BaseModel):
    topic: str
    language: str = "en"

class ReverseGeocodeRequest(BaseModel):
    latitude: float
    longitude: float

class FeedbackRequest(BaseModel):
    query_id: str
    helpful: bool
    feedback_text: Optional[str] = None
    feedback_type: Optional[str] = "general"  # general, accepted, rejected, corrected, outcome_reported
    crop: Optional[str] = None
    outcome_result: Optional[str] = None      # success, failure, partial
    outcome_reason: Optional[str] = None
    correction_previous: Optional[str] = None
    correction_new: Optional[str] = None

class RecommendationRequest(BaseModel):
    query: str
    crop: Optional[str] = None
    season: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = "en"

class MemoryCompareRequest(BaseModel):
    query: str = "What crop should I grow this season?"
    location: Optional[str] = None
    language: Optional[str] = "en"

class CommunityReportRequest(BaseModel):
    report_type: str  # pest, disease, weather, success
    crop: Optional[str] = None
    description: str
    severity: Optional[str] = "medium"  # low, medium, high
    language: str = "en"

class MemoryRetainRequest(BaseModel):
    memory_type: str
    content: str
    metadata: Optional[dict] = None
    source: Optional[str] = "farmer"
    crop: Optional[str] = None
    location: Optional[str] = None
    season: Optional[str] = None
    confidence: Optional[float] = 1.0

class MemoryRecallRequest(BaseModel):
    query: str
    memory_types: Optional[list] = None
    limit: Optional[int] = 10

# Auth functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number = payload.get("sub")
        response = users_table.get_item(Key={'phone_number': phone_number})
        user = response.get('Item')
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

def ensure_demo_farmer():
    """Ensure the designated demo farmer account exists in Azure Table Storage."""
    try:
        res = users_table.get_item(Key={'phone_number': '+919999999001'})
        if not res.get('Item'):
            hashed_password = bcrypt.hashpw("demoPassword123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            users_table.put_item(Item={
                "phone_number": "+919999999001",
                "password": hashed_password,
                "language": "hi",
                "location": "Sehore, Madhya Pradesh, India",
                "created_at": datetime.utcnow().isoformat()
            })
            print("🌱 Seeded demo farmer account (+919999999001) in Azure Table Storage")
    except Exception as e:
        print(f"Failed to ensure demo farmer account: {e}")

def ensure_community_seed_data():
    """Ensure realistic agricultural community reports and village trust scores exist in Azure Table Storage."""
    try:
        res = community_reports_table.scan(Limit=5)
        items = res.get('Items', [])
        if len(items) < 5:
            from seed_community_data import seed_community
            seed_community()
            print("🌾 Seeded realistic agricultural community reports and village trust records")
    except Exception as e:
        print(f"Failed to ensure community seed data: {e}")

@app.on_event("startup")
async def startup_event():
    print("Database tables ready (Azure Table Storage)")
    ensure_demo_farmer()
    ensure_community_seed_data()

@app.on_event("shutdown")
async def shutdown_event():
    try:
        svc = get_memory_service()
        svc.close()
    except Exception as e:
        print(f"Memory service cleanup on shutdown: {e}")

# Routes
@app.get("/")
async def root():
    return {"message": "Sarthi API with Azure Table Storage is running"}

@app.get("/health")
async def health():
    try:
        users_table.table_status
        return {"status": "healthy", "database": "connected (Azure Table Storage)"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# WhatsApp Webhook Verification
@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Verify WhatsApp webhook subscription"""
    print(f"Webhook verification attempt: mode={hub_mode}, token_match={hub_verify_token == WHATSAPP_VERIFY_TOKEN}")
    
    if not WHATSAPP_VERIFY_TOKEN:
        print("ERROR: WHATSAPP_VERIFY_TOKEN not configured")
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        print("✅ Webhook verified successfully")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    
    print(f"❌ Webhook verification failed: mode={hub_mode}, token_provided={bool(hub_verify_token)}")
    raise HTTPException(status_code=403, detail="Verification failed")

# WhatsApp Webhook Handler
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    try:
        body = await request.json()
        print(f"📱 WhatsApp webhook received: {body}")
        
        # Validate webhook structure
        if not body.get("entry"):
            print("⚠️ Invalid webhook: missing 'entry' field")
            return JSONResponse({"status": "received"}, status_code=200)
        
        # Quick response to avoid Meta retries (must respond within 20s)
        asyncio.create_task(process_whatsapp_message(body))
        
        return JSONResponse({"status": "received"}, status_code=200)
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        # Always return 200 to prevent Meta retries
        return JSONResponse({"status": "error", "message": str(e)}, status_code=200)

async def process_whatsapp_message(body: dict):
    """Process WhatsApp message asynchronously"""
    try:
        entry = body.get("entry", [])
        if not entry:
            print("⚠️ No entry in webhook body")
            return
        
        changes = entry[0].get("changes", [])
        if not changes:
            print("⚠️ No changes in entry")
            return
        
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            print("⚠️ No messages in value (might be status update)")
            return
        
        message = messages[0]
        sender = message.get("from")
        message_type = message.get("type")
        
        if not sender:
            print("⚠️ No sender in message")
            return
        
        print(f"📨 Message from {sender}, type: {message_type}")
        
        # Only process text messages
        if message_type != "text":
            await send_whatsapp_message(sender, "Sorry, I can only process text messages at the moment. Please send your question as text.")
            return
        
        message_text = message.get("text", {}).get("body", "").strip()
        
        if not message_text:
            print("⚠️ Empty message text")
            return
        
        print(f"💬 Processing: '{message_text[:100]}...'")
        
        # Get or create user (use phone number as identifier)
        user = await get_or_create_whatsapp_user(sender)
        
        # Process with AI
        ai_response = await process_ai_query(message_text, user)
        
        # Send response back to WhatsApp
        await send_whatsapp_message(sender, ai_response)
        print(f"✅ Response sent to {sender}")
        
    except Exception as e:
        print(f"❌ Process WhatsApp message error: {e}")
        import traceback
        traceback.print_exc()

def normalize_phone_number(phone: str) -> str:
    """Remove country code from WhatsApp phone number"""
    # WhatsApp sends: 919032611376, DB has: 9032611376
    if phone.startswith('91') and len(phone) > 10:
        return phone[2:]  # Remove '91' country code
    return phone

async def get_or_create_whatsapp_user(phone_number: str) -> dict:
    """Get existing user or create new one for WhatsApp"""
    try:
        # Try with normalized phone (without country code)
        normalized_phone = normalize_phone_number(phone_number)
        
        response = users_table.get_item(Key={'phone_number': normalized_phone})
        user = response.get('Item')
        
        if user:
            print(f"👤 Found existing user: {normalized_phone}")
            return user
        
        # Try with original phone number
        response = users_table.get_item(Key={'phone_number': phone_number})
        user = response.get('Item')
        
        if user:
            print(f"👤 Found existing user: {phone_number}")
            return user
        
        # Create new user with default settings
        new_user = {
            "phone_number": normalized_phone,
            "password": "",  # No password for WhatsApp users
            "language": "en",
            "location": "India",
            "created_at": datetime.utcnow().isoformat(),
            "source": "whatsapp",
            "whatsapp_id": phone_number  # Store original WhatsApp ID
        }
        
        users_table.put_item(Item=new_user)
        print(f"✨ Created new WhatsApp user: {normalized_phone} (original: {phone_number})")
        
        return new_user
    except Exception as e:
        print(f"❌ Get/create user error: {e}")
        import traceback
        traceback.print_exc()
        # Return fallback user to prevent crashes
        return {
            "phone_number": normalize_phone_number(phone_number),
            "language": "en",
            "location": "India",
            "source": "whatsapp"
        }

async def process_ai_query(text: str, user: dict) -> str:
    """Process user query with AI - routes to specialized endpoints like GUI"""
    try:
        user_location = user.get("location", "India")
        language = user.get("language", "en")
        user_phone = user.get("phone_number", "Unknown")
        text_lower = text.lower()
        
        # Build user context for AI
        user_context = f"User phone: {user_phone}, Location: {user_location}, Language: {language}"
        
        # Detect intent and route to specialized endpoints
        # Weather queries
        if any(word in text_lower for word in ['weather', 'temperature', 'rain', 'climate', 'मौसम', 'बारिश', 'तापमान']):
            return await handle_weather_query(text, user, language)
        
        # Crop price queries
        elif any(word in text_lower for word in ['price', 'cost', 'rate', 'market', 'mandi', 'कीमत', 'दाम', 'भाव', 'मंडी']):
            return await handle_crop_price_query(text, user, language)
        
        # Government scheme queries
        elif any(word in text_lower for word in ['scheme', 'subsidy', 'loan', 'government', 'योजना', 'सब्सिडी', 'ऋण', 'सरकार']):
            return await handle_scheme_query(text, user, language)
        
        # Personal info queries (who am i, my profile, etc.)
        elif any(word in text_lower for word in ['who am i', 'my profile', 'my details', 'my info', 'about me', 'मैं कौन', 'मेरी जानकारी']):
            language_name = LANGUAGE_NAMES.get(language, "English")
            response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": f"You are Sarthi assistant. Tell the user about their profile in {language_name} language. Be friendly and concise."},
                    {"role": "user", "content": f"Tell me about my profile. My details: Phone: {user_phone}, Location: {user_location}, Preferred Language: {language_name}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content
        
        # General farming query
        else:
            response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": f"You are Sarthi, AI Voice Assistant for Rural India. Help with farming, weather, crops, and government schemes. {user_context}. Keep responses concise for WhatsApp (under 300 words)."},
                    {"role": "user", "content": text}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            
            # Log query to DynamoDB
            query_id = str(uuid.uuid4())
            query_english = translate_to_english(text, language)
            
            query_item = {
                "query_id": query_id,
                "user_phone": user["phone_number"],
                "query": text,
                "query_english": query_english,
                "response": response_text,
                "query_type": "whatsapp",
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "helpful": None,
                "feedback_text": None
            }
            queries_table.put_item(Item=query_item)
            
            return response_text
    except Exception as e:
        print(f"AI query error: {e}")
        return "Sorry, I'm having trouble processing your request. Please try again."

async def handle_weather_query(text: str, user: dict, language: str) -> str:
    """Handle weather queries using the same logic as /api/weather"""
    try:
        location = user.get("location", "Delhi")
        city = location.split(",")[0].strip()
        
        print(f"Weather query - User location: {location}, City: {city}")
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            print("ERROR: OpenWeather API key not found")
            return "Sorry, weather service is not configured. Please try again later."
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        print(f"Weather API URL: {url}")
        
        res = requests.get(url, timeout=10)
        print(f"Weather API response status: {res.status_code}")
        
        if res.status_code == 404:
            # Try with fallback city if location has multiple parts
            location_parts = location.split(",")
            if len(location_parts) > 1:
                fallback_city = location_parts[1].strip()
                print(f"Trying fallback city: {fallback_city}")
                url = f"https://api.openweathermap.org/data/2.5/weather?q={fallback_city}&appid={api_key}&units=metric"
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    city = fallback_city
        
        if res.status_code != 200:
            print(f"Weather API error: {res.status_code} - {res.text}")
            return f"Sorry, I couldn't find weather information for {city}. Please update your location in settings."
        
        data = res.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        print(f"Weather data: {weather_desc}, {temp}°C, {humidity}% humidity")
        
        language_name = LANGUAGE_NAMES.get(language, "English")
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a weather assistant. Provide weather information in {language_name} language ONLY. Be concise and natural for WhatsApp."},
                {"role": "user", "content": f"Tell me the weather in {city}: {weather_desc}, temperature {temp}°C, humidity {humidity}%"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"Weather response generated: {response_text[:100]}...")
        return response_text
    except Exception as e:
        print(f"Weather query error: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, I couldn't fetch weather information right now."

async def handle_crop_price_query(text: str, user: dict, language: str) -> str:
    """Handle crop price queries using the same logic as /api/crop-prices"""
    try:
        print(f"Crop price query: {text}")
        
        # Extract crop name from query using AI
        crop_extraction = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Extract the crop name from the user's query. Return only the crop name in English (e.g., wheat, rice, tomato, onion). If no crop is mentioned, return 'wheat'."},
                {"role": "user", "content": text}
            ],
            max_tokens=20,
            temperature=0.3
        )
        
        crop = crop_extraction.choices[0].message.content.strip().lower()
        location = user.get("location", "Delhi")
        market = location.split(",")[0]
        
        print(f"Extracted crop: {crop}, Market: {market}")
        
        base_prices = {
            'wheat': 2000, 'rice': 2400, 'corn': 1600, 'barley': 1800,
            'sugarcane': 5000, 'cotton': 6000, 'soybean': 4400, 'mustard': 5600,
            'onion': 3000, 'potato': 1400, 'tomato': 3600, 'chili': 8000
        }
        
        price = base_prices.get(crop, 2500)
        
        language_name = LANGUAGE_NAMES.get(language, "English")
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a crop price assistant. Provide crop price information in {language_name} language ONLY. Be concise for WhatsApp."},
                {"role": "user", "content": f"Tell me the current price of {crop} in {market} market is ₹{price} per quintal"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"Crop price response: {response_text[:100]}...")
        return response_text
    except Exception as e:
        print(f"Crop price query error: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, I couldn't fetch crop price information right now."

async def handle_scheme_query(text: str, user: dict, language: str) -> str:
    """Handle government scheme queries using the same logic as /api/gov-schemes"""
    try:
        language_name = LANGUAGE_NAMES.get(language, "English")
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are Sarthi, AI assistant for rural India. Provide information about government schemes for farmers in {language_name} language ONLY. Be concise and helpful for WhatsApp (under 300 words)."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Scheme query error: {e}")
        return "Sorry, I couldn't fetch scheme information right now."

async def send_whatsapp_message(to: str, message: str):
    """Send message to WhatsApp user via Graph API"""
    try:
        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            print("❌ WhatsApp credentials not configured")
            return
        
        # Truncate message if too long (WhatsApp limit: 4096 chars)
        if len(message) > 4000:
            message = message[:3997] + "..."
        
        url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Message sent to {to}")
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Send WhatsApp message error: {e}")
        import traceback
        traceback.print_exc()

@app.get("/api/location")
async def get_location():
    try:
        url = "http://ipapi.co/json/"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "country": data.get("country_name", "Unknown"),
                "location": f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
            }
        else:
            return {"location": "Location not available"}
    except Exception as e:
        print(f"Location API error: {e}")
        return {"location": "Delhi, India"}

@app.post("/api/reverse-geocode")
async def reverse_geocode(request: ReverseGeocodeRequest):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={request.latitude}&lon={request.longitude}&zoom=18&addressdetails=1"
        
        headers = {
            'User-Agent': 'GramVaani-App/1.0 (contact@gramvaani.com)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'address' in data:
                address_parts = data['address']
                
                village = address_parts.get('village', '')
                town = address_parts.get('town', '')
                city = address_parts.get('city', '')
                district = address_parts.get('state_district', '')
                state = address_parts.get('state', '')
                postcode = address_parts.get('postcode', '')
                
                address_components = []
                
                if village:
                    address_components.append(village)
                elif town:
                    address_components.append(town)
                elif city:
                    address_components.append(city)
                    
                if district and district not in address_components:
                    address_components.append(district)
                    
                if state:
                    address_components.append(state)
                    
                if postcode:
                    address_components.append(postcode)
                
                precise_address = ', '.join(filter(None, address_components))
                
                return {
                    "address": precise_address,
                    "coordinates": {
                        "latitude": request.latitude,
                        "longitude": request.longitude
                    }
                }
            else:
                return {"address": f"Coordinates: {request.latitude:.4f}, {request.longitude:.4f}"}
        else:
            return {"address": f"Coordinates: {request.latitude:.4f}, {request.longitude:.4f}"}
            
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return {"address": f"Coordinates: {request.latitude:.4f}, {request.longitude:.4f}"}

@app.post("/api/signup", response_model=Token)
async def signup(user: UserSignup):
    try:
        response = users_table.get_item(Key={'phone_number': user.phone_number})
        if response.get('Item'):
            raise HTTPException(status_code=400, detail="Phone number already registered")
        
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        users_table.put_item(Item={
            "phone_number": user.phone_number,
            "password": hashed_password.decode('utf-8'),
            "language": user.language,
            "location": user.location,
            "created_at": datetime.utcnow().isoformat()
        })
        
        access_token = create_access_token(data={"sub": user.phone_number})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login", response_model=Token)
async def login(user: UserLogin):
    try:
        print(f"Login attempt for: {user.phone_number}")
        
        # Ensure demo farmer exists if demo phone is used
        if user.phone_number == "+919999999001":
            ensure_demo_farmer()

        response = users_table.get_item(Key={'phone_number': user.phone_number})
        db_user = response.get('Item')
        
        if not db_user and user.phone_number == "+919999999001":
            ensure_demo_farmer()
            response = users_table.get_item(Key={'phone_number': user.phone_number})
            db_user = response.get('Item')

        if not db_user:
            print(f"User not found: {user.phone_number}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        stored_password = db_user["password"]
        
        # Allow demo password matching
        is_demo_pass = (user.phone_number == "+919999999001" and user.password in ("demoPassword123!", "demo123"))

        if not is_demo_pass:
            if stored_password.startswith('$2b$'):
                if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
                    print(f"Invalid password for: {user.phone_number}")
                    raise HTTPException(status_code=401, detail="Invalid credentials")
            else:
                if user.password != stored_password:
                    print(f"Invalid password for: {user.phone_number}")
                    raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.phone_number})
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions_table.put_item(Item={
            "session_id": session_id,
            "user_phone": user.phone_number,
            "login_time": datetime.utcnow().isoformat(),
            "query_ids": []  # Will store query IDs
        })
        
        print(f"Login successful for: {user.phone_number}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "phone_number": current_user["phone_number"],
        "language": current_user["language"],
        "location": current_user["location"]
    }

class ProfileUpdate(BaseModel):
    phone_number: Optional[str] = None
    language: Optional[str] = None
    location: Optional[str] = None

@app.put("/api/profile")
async def update_profile(profile: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    try:
        update_data = {}
        if profile.language:
            update_data["language"] = profile.language
        if profile.location:
            update_data["location"] = profile.location
        
        if update_data:
            users_table.update_item(
                Key={'phone_number': current_user["phone_number"]},
                UpdateExpression='SET ' + ', '.join([f'{k} = :{k}' for k in update_data.keys()]),
                ExpressionAttributeValues={f':{k}': v for k, v in update_data.items()}
            )
        
        return {"status": "success", "message": "Profile updated"}
    except Exception as e:
        print(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/query-history")
async def get_query_history(current_user: dict = Depends(get_current_user)):
    """Fetch user's query history from DynamoDB"""
    try:
        from boto3.dynamodb.conditions import Key
        
        response = queries_table.query(
            IndexName='user_phone-index',
            KeyConditionExpression=Key('user_phone').eq(current_user["phone_number"]),
            ScanIndexForward=False,  # Sort by timestamp descending
            Limit=50  # Last 50 queries
        )
        
        queries = response.get('Items', [])
        return {"queries": queries, "count": len(queries)}
    except Exception as e:
        print(f"Query history error: {e}")
        return {"queries": [], "count": 0}

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    """Submit feedback for a query response with Phase 4 long-term learning integration."""
    try:
        # Update query with feedback in DynamoDB if available
        try:
            queries_table.update_item(
                Key={'query_id': feedback.query_id},
                UpdateExpression='SET helpful = :h, feedback_text = :f, feedback_time = :t',
                ExpressionAttributeValues={
                    ':h': feedback.helpful,
                    ':f': feedback.feedback_text or '',
                    ':t': datetime.utcnow().isoformat()
                }
            )
        except Exception as ddb_err:
            print(f"DynamoDB feedback logging error: {ddb_err}")
        
        # Update village trust score
        try:
            village_id = current_user.get('location', 'Unknown').split(',')[0].strip()
            update_village_trust(village_id, feedback.helpful)
        except Exception as vt_err:
            print(f"Village trust update error: {vt_err}")

        # Phase 4: Long-Term Memory Learning Loop
        farmer_id = current_user.get("phone_number", "unknown")
        recommender = get_recommender()
        memory_result = recommender.process_structured_feedback(
            farmer_id=farmer_id,
            feedback=feedback.model_dump(),
        )
        
        return {
            "status": "success",
            "message": "Feedback recorded",
            "memory_retained": memory_result is not None,
            "memory_id": memory_result.get("id") if memory_result else None
        }
    except Exception as e:
        print(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def update_village_trust(village_id: str, helpful: bool):
    """Update village trust score based on feedback"""
    try:
        from boto3.dynamodb.conditions import Key
        
        # Get or create village trust record
        response = village_trust_table.get_item(Key={'village_id': village_id})
        
        if response.get('Item'):
            item = response['Item']
            total = item.get('total_responses', 0) + 1
            helpful_count = item.get('helpful_count', 0) + (1 if helpful else 0)
        else:
            total = 1
            helpful_count = 1 if helpful else 0
        
        trust_score = (helpful_count / total) * 100 if total > 0 else 0
        
        village_trust_table.put_item(Item={
            'village_id': village_id,
            'total_responses': total,
            'helpful_count': helpful_count,
            'trust_score': round(trust_score, 2),
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        print(f"Village trust update error: {e}")

@app.get("/api/village-trust/{village_id}")
async def get_village_trust(village_id: str):
    """Get village trust score"""
    try:
        response = village_trust_table.get_item(Key={'village_id': village_id})
        if response.get('Item'):
            return response['Item']
        return {
            'village_id': village_id,
            'total_responses': 0,
            'helpful_count': 0,
            'trust_score': 0
        }
    except Exception as e:
        print(f"Village trust fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/community-report")
async def submit_community_report(report: CommunityReportRequest, current_user: dict = Depends(get_current_user)):
    """Submit a community report (pest, disease, weather observation, success story)"""
    try:
        report_id = str(uuid.uuid4())
        village_id = current_user.get('location', 'Unknown').split(',')[0].strip()
        
        # Translate description to English
        description_english = translate_to_english(report.description, report.language)
        
        report_item = {
            'report_id': report_id,
            'user_phone': current_user['phone_number'],
            'village_id': village_id,
            'report_type': report.report_type,
            'crop': report.crop or 'general',
            'description': report.description,
            'description_english': description_english,
            'severity': report.severity,
            'language': report.language,
            'timestamp': datetime.utcnow().isoformat(),
            'verified': False,
            'validation_count': 0,
            'validators': []
        }
        
        community_reports_table.put_item(Item=report_item)
        
        # Check for outbreak pattern (5+ reports in same village within 7 days)
        from boto3.dynamodb.conditions import Key
        from datetime import timedelta
        
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent_reports = community_reports_table.query(
            IndexName='village_id-timestamp-index',
            KeyConditionExpression=Key('village_id').eq(village_id) & Key('timestamp').gt(week_ago),
            FilterExpression='report_type = :rt',
            ExpressionAttributeValues={':rt': report.report_type}
        )
        
        outbreak_detected = len(recent_reports.get('Items', [])) >= 5
        
        return {
            'status': 'success',
            'report_id': report_id,
            'message': 'Report submitted successfully',
            'outbreak_alert': outbreak_detected,
            'similar_reports': len(recent_reports.get('Items', []))
        }
    except Exception as e:
        print(f"Community report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/community-reports")
async def get_community_reports(current_user: dict = Depends(get_current_user), limit: int = 50):
    """Get recent community reports - show all reports if no village-specific index"""
    try:
        # Try to get all reports (fallback if index doesn't exist)
        response = community_reports_table.scan(Limit=limit)
        reports = response.get('Items', [])
        
        # Sort by timestamp (most recent first)
        reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {'reports': reports[:limit], 'count': len(reports)}
    except Exception as e:
        print(f"Fetch reports error: {e}")
        return {'reports': [], 'count': 0}

@app.post("/api/validate-report/{report_id}")
async def validate_report(report_id: str, helpful: bool, current_user: dict = Depends(get_current_user)):
    """Peer validation: farmers validate other farmers' reports"""
    try:
        response = community_reports_table.get_item(Key={'report_id': report_id})
        report = response.get('Item')
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        validators = report.get('validators', [])
        user_phone = current_user['phone_number']
        
        # Prevent duplicate validation
        if user_phone in validators:
            return {'status': 'already_validated', 'message': 'You have already validated this report'}
        
        validators.append(user_phone)
        validation_count = report.get('validation_count', 0) + (1 if helpful else 0)
        
        # Mark as verified if 3+ farmers validate
        verified = len(validators) >= 3 and validation_count >= 2
        
        community_reports_table.update_item(
            Key={'report_id': report_id},
            UpdateExpression='SET validators = :v, validation_count = :vc, verified = :vf',
            ExpressionAttributeValues={
                ':v': validators,
                ':vc': validation_count,
                ':vf': verified
            }
        )
        
        return {
            'status': 'success',
            'verified': verified,
            'validation_count': validation_count,
            'total_validators': len(validators)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/village-leaderboard")
async def get_village_leaderboard(limit: int = 10):
    """Get top villages by trust score (Gold/Silver/Bronze)"""
    try:
        response = village_trust_table.scan()
        villages = response.get('Items', [])
        
        # Sort by trust score
        villages.sort(key=lambda x: x.get('trust_score', 0), reverse=True)
        
        # Assign tiers
        for i, village in enumerate(villages[:limit]):
            score = village.get('trust_score', 0)
            if score >= 80:
                village['tier'] = 'Gold'
                village['tier_icon'] = '🥇'
            elif score >= 60:
                village['tier'] = 'Silver'
                village['tier_icon'] = '🥈'
            else:
                village['tier'] = 'Bronze'
                village['tier_icon'] = '🥉'
            village['rank'] = i + 1
        
        return {'leaderboard': villages[:limit], 'total_villages': len(villages)}
    except Exception as e:
        print(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crop-calendar")
async def get_crop_calendar(current_user: dict = Depends(get_current_user), language: str = "en"):
    """Get crop calendar with planting and harvesting schedules"""
    try:
        import json
        
        # Load crop calendar data
        with open('crop_calendar.json', 'r') as f:
            calendar_data = json.load(f)
        
        # Get current season
        month = datetime.utcnow().month
        season_map = calendar_data.get('current_season_info', {})
        current_season = season_map.get(str(month), 'rabi')
        
        # Get user location and weather
        user_location = current_user.get('location', 'India')
        city = user_location.split(',')[0].strip()
        
        # Fetch weather data
        weather_info = None
        try:
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if api_key:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    weather_info = {
                        'temp': round(data['main']['temp']),
                        'humidity': data['main']['humidity'],
                        'description': data['weather'][0]['description']
                    }
        except Exception as e:
            print(f"Weather fetch error: {e}")
        
        # Filter crops by current season
        all_crops = calendar_data.get('crops', {})
        recommended_crops = []
        
        for crop_id, crop_info in all_crops.items():
            crop_season = crop_info.get('season', '')
            if crop_season == current_season or crop_season == 'year-round':
                crop_data = {
                    'id': crop_id,
                    'name': crop_info.get('name'),
                    'hindi': crop_info.get('hindi'),
                    'planting': crop_info.get('planting'),
                    'harvesting': crop_info.get('harvesting'),
                    'duration_days': crop_info.get('duration_days'),
                    'tips': crop_info.get('tips'),
                    'soil_type': crop_info.get('soil_type', 'Well-drained loamy soil'),
                    'rainfall': crop_info.get('rainfall', 'Moderate')
                }
                recommended_crops.append(crop_data)
        
        # Fast translate using Amazon Translate if not English
        if language != 'en' and recommended_crops:
            try:
                print(f"Translating {len(recommended_crops)} crops to {language}")
                for crop in recommended_crops:
                    # Translate crop name
                    name_result = translate_client.translate_text(
                        Text=crop['name'],
                        SourceLanguageCode='en',
                        TargetLanguageCode=language
                    )
                    # Translate tips
                    tips_result = translate_client.translate_text(
                        Text=crop['tips'],
                        SourceLanguageCode='en',
                        TargetLanguageCode=language
                    )
                    # Translate soil type
                    soil_result = translate_client.translate_text(
                        Text=crop['soil_type'],
                        SourceLanguageCode='en',
                        TargetLanguageCode=language
                    )
                    # Translate rainfall
                    rainfall_result = translate_client.translate_text(
                        Text=crop['rainfall'],
                        SourceLanguageCode='en',
                        TargetLanguageCode=language
                    )
                    
                    # Translate planting months
                    if crop.get('planting'):
                        planting_start = translate_client.translate_text(
                            Text=crop['planting']['start'],
                            SourceLanguageCode='en',
                            TargetLanguageCode=language
                        )
                        planting_end = translate_client.translate_text(
                            Text=crop['planting']['end'],
                            SourceLanguageCode='en',
                            TargetLanguageCode=language
                        )
                        crop['planting']['start'] = planting_start['TranslatedText']
                        crop['planting']['end'] = planting_end['TranslatedText']
                    
                    # Translate harvesting months
                    if crop.get('harvesting'):
                        harvest_start = translate_client.translate_text(
                            Text=crop['harvesting']['start'],
                            SourceLanguageCode='en',
                            TargetLanguageCode=language
                        )
                        harvest_end = translate_client.translate_text(
                            Text=crop['harvesting']['end'],
                            SourceLanguageCode='en',
                            TargetLanguageCode=language
                        )
                        crop['harvesting']['start'] = harvest_start['TranslatedText']
                        crop['harvesting']['end'] = harvest_end['TranslatedText']
                    
                    print(f"Translated {crop['name']} -> {name_result['TranslatedText']}")
                    crop['name'] = name_result['TranslatedText']
                    crop['tips'] = tips_result['TranslatedText']
                    crop['soil_type'] = soil_result['TranslatedText']
                    crop['rainfall'] = rainfall_result['TranslatedText']
                print(f"Translation complete for {language}")
            except Exception as e:
                print(f"Amazon Translate error: {e}")
                import traceback
                traceback.print_exc()
        
        return {
            'current_season': current_season,
            'user_location': user_location,
            'weather': weather_info,
            'recommended_crops': recommended_crops
        }
    except Exception as e:
        print(f"Crop calendar error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hyperlocal-context")
async def get_hyperlocal_context(current_user: dict = Depends(get_current_user)):
    """Get hyperlocal agricultural context based on user location"""
    try:
        location = current_user.get("location", "")
        parts = [p.strip() for p in location.split(",")]
        
        # Try to match district or state
        query = {}
        if len(parts) >= 2:
            query = {"$or": [{"district": {"$regex": parts[0], "$options": "i"}}, {"state": {"$regex": parts[1], "$options": "i"}}]}
        elif len(parts) == 1:
            query = {"$or": [{"district": {"$regex": parts[0], "$options": "i"}}, {"state": {"$regex": parts[0], "$options": "i"}}]}
        
        context = hyperlocal_collection.find_one(query)
        
        if not context:
            return {"message": "No hyperlocal data available for your location", "has_data": False}
        
        # Get current season
        month = datetime.utcnow().month
        if month in [6, 7, 8, 9, 10]:  # June-Oct
            season = "kharif"
        elif month in [11, 12, 1, 2, 3]:  # Nov-Mar
            season = "rabi"
        else:
            season = "summer"
        
        return {
            "has_data": True,
            "location": f"{context['district']}, {context['state']}",
            "soil_type": context["soil_type"],
            "rainfall": context["rainfall"],
            "current_season": season,
            "recommended_crops": context["crops"].get(season, []),
            "all_crops": context["crops"],
            "pest_alerts": context.get("pest_alerts", [])
        }
    except Exception as e:
        print(f"Hyperlocal context error: {e}")
        return {"has_data": False, "message": "Error fetching hyperlocal data"}

@app.get("/api/success-stories")
async def get_success_stories(current_user: dict = Depends(get_current_user), limit: int = 10):
    """Get nearby farmer success stories"""
    try:
        location = current_user.get("location", "")
        
        # Find stories from same region
        stories = list(success_stories_collection.find(
            {"location": {"$regex": location.split(",")[0], "$options": "i"}}
        ).limit(limit))
        
        # If no local stories, get any stories
        if not stories:
            stories = list(success_stories_collection.find().limit(limit))
        
        for story in stories:
            story["_id"] = str(story["_id"])
        
        return {"stories": stories, "count": len(stories)}
    except Exception as e:
        print(f"Success stories error: {e}")
        return {"stories": [], "count": 0}

@app.post("/api/report-pest-outbreak")
async def report_pest_outbreak(current_user: dict = Depends(get_current_user), pest_name: str = "", crop: str = "", severity: str = "medium"):
    """Report pest outbreak for location clustering"""
    try:
        location = current_user.get("location", "Unknown")
        
        outbreak = {
            "user_phone": current_user["phone_number"],
            "location": location,
            "pest_name": pest_name,
            "crop": crop,
            "severity": severity,
            "timestamp": datetime.utcnow(),
            "verified": False
        }
        
        pest_outbreaks_collection.insert_one(outbreak)
        
        # Check for clustering (3+ reports in same area within 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        nearby_reports = pest_outbreaks_collection.count_documents({
            "location": {"$regex": location.split(",")[0], "$options": "i"},
            "pest_name": pest_name,
            "timestamp": {"$gte": week_ago}
        })
        
        alert = nearby_reports >= 3
        
        return {
            "status": "success",
            "outbreak_alert": alert,
            "nearby_reports": nearby_reports,
            "message": f"Outbreak alert! {nearby_reports} reports in your area" if alert else "Report submitted"
        }
    except Exception as e:
        print(f"Pest outbreak report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/outbreak-map")
async def get_outbreak_map(current_user: dict = Depends(get_current_user), language: str = "en"):
    """Get pest/disease outbreak patterns across villages with geographic clustering"""
    try:
        from collections import defaultdict
        
        # Get all reports
        response = community_reports_table.scan(Limit=100)
        reports = response.get('Items', [])
        
        GEO_COORDINATES = {
            "Sehore": {"lat": 23.2032, "lng": 77.0844, "state": "Madhya Pradesh"},
            "Guntur": {"lat": 16.3067, "lng": 80.4365, "state": "Andhra Pradesh"},
            "Nashik": {"lat": 19.9975, "lng": 73.7898, "state": "Maharashtra"},
            "Warangal": {"lat": 17.9689, "lng": 79.5941, "state": "Telangana"},
            "Karnal": {"lat": 29.6857, "lng": 76.9905, "state": "Haryana"},
            "Coimbatore": {"lat": 11.0168, "lng": 76.9558, "state": "Tamil Nadu"},
            "India": {"lat": 20.5937, "lng": 78.9629, "state": "National"}
        }
        
        # Group by village and type
        outbreak_data = defaultdict(lambda: {'pest': 0, 'disease': 0, 'weather': 0, 'success': 0, 'reports': []})
        
        for report in reports:
            village = report.get('village_id', 'Unknown')
            report_type = report.get('report_type', '')
            if report_type in ('pest', 'disease', 'weather', 'success'):
                outbreak_data[village][report_type] += 1
            else:
                outbreak_data[village][report_type] = 1
                
            if report_type in ('pest', 'disease'):
                outbreak_data[village]['reports'].append({
                    'type': report_type,
                    'crop': report.get('crop'),
                    'description': report.get('description_english', report.get('description')),
                    'severity': report.get('severity'),
                    'timestamp': report.get('timestamp')
                })
        
        # Identify outbreaks (2+ pest/disease reports constitutes an active monitored hotspot)
        outbreaks = []
        language_name = LANGUAGE_NAMES.get(language, 'English')
        
        for village, data in outbreak_data.items():
            pest_cnt = data.get('pest', 0)
            dis_cnt = data.get('disease', 0)
            total = pest_cnt + dis_cnt
            if total >= 2:
                geo = GEO_COORDINATES.get(village, {"lat": 20.5937, "lng": 78.9629, "state": "India"})
                
                # Dynamic alert levels based on report intensity
                if total >= 4:
                    alert_level = 'high'
                elif total >= 3:
                    alert_level = 'medium'
                else:
                    alert_level = 'low'
                    
                # Collect crops affected
                crops = list(set([r.get('crop') for r in data['reports'] if r.get('crop')]))
                
                # Translate village name if not English
                translated_village = village
                if language != 'en':
                    try:
                        translation_response = azure_client.chat.completions.create(
                            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                            messages=[
                                {"role": "system", "content": f"Translate this place name to {language_name}. Return ONLY the translated name."},
                                {"role": "user", "content": village}
                            ],
                            max_tokens=20,
                            temperature=0.3
                        )
                        translated_village = translation_response.choices[0].message.content.strip()
                    except Exception as e:
                        print(f"Village name translation error: {e}")
                
                outbreaks.append({
                    'village': translated_village,
                    'state': geo.get('state', 'India'),
                    'coordinates': {'lat': geo['lat'], 'lng': geo['lng']},
                    'pest_count': pest_cnt,
                    'disease_count': dis_cnt,
                    'total_reports': total,
                    'alert_level': alert_level,
                    'crops_affected': crops,
                    'recent_reports': data['reports'][:5]
                })
        
        # Sort outbreaks by alert severity and total reports descending
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        outbreaks.sort(key=lambda x: (severity_order.get(x['alert_level'], 0), x['total_reports']), reverse=True)
        
        return {
            'outbreaks': outbreaks,
            'total_reports': len(reports),
            'affected_villages': len(outbreaks)
        }
    except Exception as e:
        print(f"Outbreak map error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-text")
async def process_text(request: TextRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_location = current_user.get("location", "India")
        farmer_id = current_user.get("phone_number", "unknown")
        recommender = get_recommender()
        print(f"Process text for farmer {farmer_id}: {request.text[:50]}...")
        
        # Phase 4: Detect and retain durable conversational learning (outcomes, failures, constraints)
        retained_learning = None
        try:
            retained_learning = recommender.detect_and_retain_conversational_learning(farmer_id, request.text)
        except Exception as retain_err:
            print(f"Conversational learning retain error (non-fatal): {retain_err}")

        # Phase 3: Targeted Memory Retrieval & Assembly (with precedence policy)
        assembled_context = {}
        raw_memories = []
        memory_prompt_section = ""
        try:
            assembled_context, raw_memories = recommender.assemble_memory_context(
                farmer_id=farmer_id,
                query=request.text,
                location=user_location,
            )
            memory_prompt_section = recommender.format_memory_for_prompt(assembled_context)
        except Exception as recall_err:
            print(f"Hindsight recall error (fallback to standard context): {recall_err}")

        # OPTIMIZED: Fetch minimal context data (use sync version in async context)
        context_data = fetch_context_sync(user_location, request.text)
        formatted_context = format_context_for_llm(context_data)
        
        print(f"Context: {len(formatted_context)} chars, Memories used: {len(raw_memories)}")
        
        # Enriched system prompt containing remembered farmer context
        system_prompt = f"""You are Sarthi, AI assistant for rural India. Use the data below to answer.

{formatted_context}
{memory_prompt_section}

Be concise and practical."""
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.text}
            ],
            max_tokens=500,  # Reduced from 1000
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        # Phase 3: Structured memory influence metadata
        memory_influence = recommender.build_memory_influence_metadata(assembled_context, response_text)
        
        # Async TTS generation
        audio_data = synthesize_speech(response_text, request.language)
        
        # Log query async (don't wait)
        query_id = str(uuid.uuid4())
        asyncio.create_task(log_query_async(query_id, current_user, request.text, response_text, request.language))

        used_types = list({m.get("type", "profile") for m in raw_memories}) if raw_memories else []
        relevant_memories = []
        for cat, items in assembled_context.items():
            for item in items:
                relevant_memories.append({
                    "id": item.get("id"),
                    "category": cat,
                    "type": item.get("type", cat),
                    "summary": item.get("text"),
                    "crop": item.get("crop"),
                })

        return JSONResponse({
            "query_id": query_id,
            "recommendation_id": query_id,
            "response_text": response_text,
            "audio_data": audio_data,
            "retained_learning": retained_learning,
            "memory_context": {
                "used": bool(raw_memories),
                "memory_count": len(raw_memories),
                "types": used_types
            },
            "relevant_memories": relevant_memories,
            "memory_influence": memory_influence
        })
    except Exception as e:
        print(f"Process text error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def log_query_async(query_id: str, user: dict, query: str, response: str, language: str):
    """Log query asynchronously without blocking response"""
    try:
        query_item = {
            "query_id": query_id,
            "user_phone": user["phone_number"],
            "query": query,
            "response": response,
            "language": language,
            "timestamp": datetime.utcnow().isoformat(),
            "helpful": None
        }
        queries_table.put_item(Item=query_item)
    except Exception as e:
        print(f"Log error: {e}")

@app.post("/api/weather")
async def get_weather(request: WeatherRequest, current_user: dict = Depends(get_current_user)):
    try:
        city = request.city
        if not city or city == 'current':
            location = current_user.get("location", "Delhi")
            city = location.split(",")[0].strip()
        
        print(f"Weather request for city: {city}, language: {request.language}")
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="OpenWeather API key not configured."
            )
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url, timeout=10)
        
        if res.status_code == 404:
            location_parts = current_user.get("location", "Delhi").split(",")
            if len(location_parts) > 1:
                fallback_city = location_parts[1].strip()
                res = requests.get(
                    f"https://api.openweathermap.org/data/2.5/weather?q={fallback_city}&appid={api_key}&units=metric",
                    timeout=10
                )
                if res.status_code == 200:
                    city = fallback_city
        
        if res.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Weather data not found for {city}")
        
        data = res.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        language_name = LANGUAGE_NAMES.get(request.language, "English")
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a weather assistant. Provide weather information in {language_name} language ONLY. Be concise and natural."},
                {"role": "user", "content": f"Tell me the weather in {city}: {weather_desc}, temperature {temp}°C, humidity {humidity}%"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"Weather response in {language_name}: {response_text}")
        
        audio_data = synthesize_speech(response_text, request.language)
        return JSONResponse({"text": response_text, "audio_data": audio_data})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Weather error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")

@app.post("/api/crop-prices")
async def get_crop_prices(request: CropPriceRequest, current_user: dict = Depends(get_current_user)):
    try:
        market = request.market or current_user.get("location", "Delhi").split(",")[0]
        
        base_prices = {
            'wheat': 2000, 'rice': 2400, 'corn': 1600, 'barley': 1800,
            'sugarcane': 5000, 'cotton': 6000, 'soybean': 4400, 'mustard': 5600,
            'onion': 3000, 'potato': 1400, 'tomato': 3600, 'chili': 8000
        }
        
        price = base_prices.get(request.crop.lower(), 2500)
        
        language_name = LANGUAGE_NAMES.get(request.language, "English")
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a crop price assistant. Provide crop price information in {language_name} language ONLY. Be concise and natural."},
                {"role": "user", "content": f"Tell me the current price of {request.crop} in {market} market is ₹{price} per quintal"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"Crop price response in {language_name}: {response_text}")
        
        audio_data = synthesize_speech(response_text, request.language)
        return JSONResponse({"text": response_text, "audio_data": audio_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/gov-schemes")
async def get_gov_schemes(request: SchemeRequest, current_user: dict = Depends(get_current_user)):
    try:
        print(f"Schemes request for topic: {request.topic}, language: {request.language}")
        
        language_name = LANGUAGE_NAMES.get(request.language, "English")
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are Sarthi, AI assistant for rural India. Provide information about government schemes for farmers in {language_name} language ONLY. Be concise and helpful."},
                {"role": "user", "content": f"Tell me about government schemes related to {request.topic}"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        print(f"Schemes response in {language_name} generated successfully")
        
        audio_data = synthesize_speech(response_text, request.language)
        return JSONResponse({"text": response_text, "audio_data": audio_data})
    except Exception as e:
        print(f"Schemes error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching schemes: {str(e)}")

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...), language: str = "hi", current_user: dict = Depends(get_current_user)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["wav", "mp3"]:
            raise HTTPException(status_code=400, detail="Only WAV and MP3 files supported")
        
        audio_bytes = await file.read()
        transcript = await transcribe_service.transcribe_audio(audio_bytes, file_extension, language)
        
        return JSONResponse({"transcript": transcript})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Transcribe error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...), language: str = "hi", current_user: dict = Depends(get_current_user)):
    try:
        print(f"Audio: {file.filename}, lang: {language}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file")
        
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["wav", "mp3", "webm", "ogg"]:
            file_extension = "wav"
        
        audio_bytes = await file.read()
        
        # Transcribe
        transcript = await transcribe_service.transcribe_audio(audio_bytes, file_extension, language)
        print(f"Transcript: {transcript[:50]}...")
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcription failed")
        
        user_location = current_user.get("location", "India")
        farmer_id = current_user.get("phone_number", "unknown")
        recommender = get_recommender()
        
        # Phase 4: Detect and retain durable conversational learning from voice
        retained_learning = None
        try:
            retained_learning = recommender.detect_and_retain_conversational_learning(farmer_id, transcript)
        except Exception as retain_err:
            print(f"Voice conversational learning retain error: {retain_err}")

        # Phase 3: Targeted Memory Retrieval & Assembly
        assembled_context = {}
        raw_memories = []
        memory_prompt_section = ""
        try:
            assembled_context, raw_memories = recommender.assemble_memory_context(
                farmer_id=farmer_id,
                query=transcript,
                location=user_location,
            )
            memory_prompt_section = recommender.format_memory_for_prompt(assembled_context)
        except Exception as recall_err:
            print(f"Voice Hindsight recall error: {recall_err}")
        
        # OPTIMIZED: Minimal context (use sync version)
        context_data = fetch_context_sync(user_location, transcript)
        formatted_context = format_context_for_llm(context_data)
        
        language_name = LANGUAGE_NAMES.get(language, "English")
        system_prompt = f"""You are Sarthi. Help with farming. User in {user_location}. Respond in {language_name} ONLY.

{formatted_context}
{memory_prompt_section}

Be concise."""
        
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript}
            ],
            max_tokens=500,  # Reduced
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        
        # Calculate structured memory influence metadata
        memory_influence = recommender.build_memory_influence_metadata(assembled_context, response_text)
        
        # Async logging
        query_id = str(uuid.uuid4())
        asyncio.create_task(log_query_async(query_id, current_user, transcript, response_text, language))
        
        audio_data = synthesize_speech(response_text, language)

        used_types = list({m.get("type", "profile") for m in raw_memories}) if raw_memories else []
        relevant_memories = []
        for cat, items in assembled_context.items():
            for item in items:
                relevant_memories.append({
                    "id": item.get("id"),
                    "category": cat,
                    "type": item.get("type", cat),
                    "summary": item.get("text"),
                    "crop": item.get("crop"),
                })

        return JSONResponse({
            "query_id": query_id,
            "recommendation_id": query_id,
            "transcript": transcript,
            "response_text": response_text,
            "audio_data": audio_data,
            "retained_learning": retained_learning,
            "memory_context": {
                "used": bool(raw_memories),
                "memory_count": len(raw_memories),
                "types": used_types
            },
            "relevant_memories": relevant_memories,
            "memory_influence": memory_influence
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Audio error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ==================== SMART FARM ADVISOR ENDPOINTS ====================

@app.get("/api/weather")
async def get_advisor_weather(current_user: dict = Depends(get_current_user)):
    """Get weather data for Advisor page"""
    try:
        location = current_user.get("location", "Delhi")
        city = location.split(",")[0].strip()
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return {"temperature": 25, "humidity": 60, "rainfall": 0, "condition": "Clear", "alert": None}
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url, timeout=10)
        
        if res.status_code != 200:
            return {"temperature": 25, "humidity": 60, "rainfall": 0, "condition": "Clear", "alert": None}
        
        data = res.json()
        
        # Check for alerts
        alert = None
        if data["main"]["temp"] > 35:
            alert = "High temperature alert. Ensure adequate irrigation."
        elif data.get("rain", {}).get("1h", 0) > 10:
            alert = "Heavy rainfall expected. Protect crops from waterlogging."
        
        return {
            "temperature": round(data["main"]["temp"]),
            "humidity": data["main"]["humidity"],
            "rainfall": data.get("rain", {}).get("1h", 0),
            "condition": data["weather"][0]["main"],
            "alert": alert
        }
    except Exception as e:
        print(f"Weather error: {e}")
        return {"temperature": 25, "humidity": 60, "rainfall": 0, "condition": "Clear", "alert": None}


@app.get("/api/agriculture-news")
async def get_agriculture_news(current_user: dict = Depends(get_current_user)):
    """Get agriculture news for Advisor page"""
    try:
        # Check MongoDB for cached news
        news = list(mongo_db.agriculture_news.find().sort("published_at", -1).limit(6))
        
        if news:
            for item in news:
                item.pop('_id', None)
            return news
        
        # Return sample news with images
        sample_news = [
            {
                "title": "New PM-KISAN Scheme Benefits Announced for Small Farmers",
                "summary": "Government announces increased financial assistance under PM-KISAN scheme. Eligible farmers will receive direct benefit transfers to support agricultural activities and improve rural livelihoods.",
                "source": "Ministry of Agriculture",
                "link": "https://pmkisan.gov.in",
                "image": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&h=200&fit=crop",
                "published_at": datetime.utcnow().isoformat()
            },
            {
                "title": "IMD Predicts Normal Monsoon Rainfall This Season",
                "summary": "India Meteorological Department forecasts normal monsoon rainfall across major agricultural regions. Farmers advised to prepare for timely sowing operations and optimize water management practices.",
                "source": "IMD Weather",
                "link": "https://mausam.imd.gov.in",
                "image": "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?w=400&h=200&fit=crop",
                "published_at": datetime.utcnow().isoformat()
            },
            {
                "title": "State Government Increases Organic Farming Subsidies",
                "summary": "New policy provides enhanced subsidies for farmers transitioning to organic farming methods. Includes support for certification, training, and market linkages to promote sustainable agriculture.",
                "source": "Agricultural Dept",
                "link": "https://agricoop.gov.in",
                "image": "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400&h=200&fit=crop",
                "published_at": datetime.utcnow().isoformat()
            },
            {
                "title": "Drip Irrigation Systems Now Available at 50% Subsidy",
                "summary": "Government launches new scheme offering 50% subsidy on drip irrigation systems. Aims to promote water conservation and improve crop yields through efficient irrigation technology.",
                "source": "Water Resources",
                "link": "https://pmksy.gov.in",
                "image": "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=400&h=200&fit=crop",
                "published_at": datetime.utcnow().isoformat()
            },
            {
                "title": "Crop Insurance Deadline Extended for Kharif Season",
                "summary": "Pradhan Mantri Fasal Bima Yojana extends registration deadline. Farmers can now enroll until the end of the month to protect their crops against natural calamities and yield losses.",
                "source": "PMFBY Portal",
                "link": "https://pmfby.gov.in",
                "image": "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=400&h=200&fit=crop",
                "published_at": datetime.utcnow().isoformat()
            },
            {
                "title": "New Mobile App Launched for Real-Time Mandi Prices",
                "summary": "Agriculture ministry launches mobile application providing real-time market prices from mandis across the country. Helps farmers make informed decisions about crop sales and market timing.",
                "source": "eNAM Platform",
                "link": "https://enam.gov.in",
                "image": "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=400&h=200&fit=crop",
                "published_at": datetime.utcnow().isoformat()
            }
        ]
        
        return sample_news
    except Exception as e:
        print(f"Agriculture news error: {e}")
        return []


@app.get("/api/environmental-profile")
async def get_environmental_profile(current_user: dict = Depends(get_current_user)):
    """Get environmental profile for current user"""
    try:
        # Check if user has profile in MongoDB
        profile = mongo_db.environmental_profiles.find_one({"user_phone": current_user["phone_number"]})
        
        if not profile:
            # Create default profile
            profile = {
                "user_phone": current_user["phone_number"],
                "location": current_user.get("location", "Unknown"),
                "temperature": 12,
                "humidity": 37,
                "rainfall": 100,
                "nitrogen": 50,
                "phosphorus": 50,
                "potassium": 50,
                "soil_ph": 8.5,
                "created_at": datetime.utcnow()
            }
            mongo_db.environmental_profiles.insert_one(profile)
        
        # Remove MongoDB _id
        profile.pop('_id', None)
        return profile
    except Exception as e:
        print(f"Environmental profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crop-recommendations")
async def get_crop_recommendations_smart(current_user: dict = Depends(get_current_user)):
    """Get AI crop recommendations based on user location"""
    try:
        location = current_user.get("location", "")
        
        # Extract region from location (city, district, or state)
        location_parts = [p.strip().lower() for p in location.split(",")]
        
        # Try to find crops suitable for user's region
        query = {}
        if location_parts:
            # Search by region in crop data
            query = {
                "$or": [
                    {"suitable_regions": {"$regex": location_parts[0], "$options": "i"}},
                    {"climate_zone": {"$regex": location_parts[0], "$options": "i"}}
                ]
            }
        
        crops = list(mongo_db.crop_recommendations.find(query).limit(10))
        
        # If no location-specific crops found, get general recommendations
        if not crops:
            crops = list(mongo_db.crop_recommendations.find().limit(10))
        
        # Get user's environmental profile for compatibility scoring
        profile = mongo_db.environmental_profiles.find_one({"user_phone": current_user["phone_number"]})
        
        if profile:
            # Calculate compatibility for each crop
            params = SoilParams(
                nitrogen=profile.get("nitrogen", 50),
                phosphorus=profile.get("phosphorus", 50),
                potassium=profile.get("potassium", 50),
                temperature=profile.get("temperature", 25),
                humidity=profile.get("humidity", 60),
                ph=profile.get("soil_ph", 7.0),
                rainfall=profile.get("rainfall", 100)
            )
            
            for crop in crops:
                crop["soil_compatibility"] = calculate_compatibility(params, crop)
            
            # Sort by compatibility
            crops.sort(key=lambda x: x.get("soil_compatibility", 0), reverse=True)
        
        for crop in crops:
            crop.pop('_id', None)
        
        return crops
    except Exception as e:
        print(f"Crop recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/optimization-strategies")
async def get_optimization_strategies(current_user: dict = Depends(get_current_user)):
    """Generate AI-powered farming optimization strategies based on location and crops"""
    try:
        location = current_user.get("location", "India")
        
        # Get user's environmental profile
        profile = mongo_db.environmental_profiles.find_one({"user_phone": current_user["phone_number"]})
        
        # Get top recommended crops
        crops = list(mongo_db.crop_recommendations.find().limit(3))
        crop_names = [c.get("crop_name", "") for c in crops]
        
        # Build context for AI
        context = f"""Location: {location}
Soil pH: {profile.get('soil_ph', 7.0) if profile else 7.0}
Temperature: {profile.get('temperature', 25) if profile else 25}°C
Humidity: {profile.get('humidity', 60) if profile else 60}%
Rainfall: {profile.get('rainfall', 100) if profile else 100}mm
Top Crops: {', '.join(crop_names)}"""
        
        # Generate strategies using AI
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are an agricultural expert. Generate 4 practical farming optimization strategies. Return ONLY a JSON array with objects containing: strategy_name, impact_level (High/Medium/Low), difficulty (Low/Medium/High), cost_effectiveness (percentage like 150%), badge (Minimal/Moderate/Peak). Be concise."},
                {"role": "user", "content": f"Generate 4 farming optimization strategies for:\n{context}"}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        import json
        strategies_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        if "```json" in strategies_text:
            strategies_text = strategies_text.split("```json")[1].split("```")[0].strip()
        elif "```" in strategies_text:
            strategies_text = strategies_text.split("```")[1].split("```")[0].strip()
        
        try:
            strategies = json.loads(strategies_text)
            return strategies
        except:
            # Fallback to database strategies if AI parsing fails
            strategies = list(mongo_db.optimization_strategies.find().limit(4))
            for strategy in strategies:
                strategy.pop('_id', None)
            return strategies
            
    except Exception as e:
        print(f"Optimization strategies error: {e}")
        # Fallback to database
        try:
            strategies = list(mongo_db.optimization_strategies.find().limit(4))
            for strategy in strategies:
                strategy.pop('_id', None)
            return strategies
        except:
            return []


@app.get("/api/farm-intelligence")
async def get_farm_intelligence(current_user: dict = Depends(get_current_user)):
    """Get farm intelligence analytics"""
    try:
        analytics = mongo_db.farm_intelligence_analytics.find_one({"user_phone": current_user["phone_number"]})
        
        if not analytics:
            # Create default analytics
            analytics = {
                "user_phone": current_user["phone_number"],
                "location": current_user.get("location", "Unknown"),
                "load_predictions": 3,
                "top_crop": "mango",
                "soil_stability": 86,
                "climate_risk": "Low",
                "feature_importance": {
                    "nitrogen": 20,
                    "phosphorus": 15,
                    "potassium": 15,
                    "temperature": 18,
                    "humidity": 12,
                    "ph": 10,
                    "rainfall": 10
                },
                "created_at": datetime.utcnow()
            }
            mongo_db.farm_intelligence_analytics.insert_one(analytics)
        
        analytics.pop('_id', None)
        return analytics
    except Exception as e:
        print(f"Farm intelligence error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SoilParams(BaseModel):
    nitrogen: int
    phosphorus: int
    potassium: int
    temperature: int
    humidity: int
    ph: float
    rainfall: int


@app.post("/api/get-crop-recommendation")
async def get_crop_recommendation_custom(params: SoilParams, current_user: dict = Depends(get_current_user)):
    """Get crop recommendation based on custom soil parameters"""
    try:
        # Update user's environmental profile
        mongo_db.environmental_profiles.update_one(
            {"user_phone": current_user["phone_number"]},
            {"$set": {
                "nitrogen": params.nitrogen,
                "phosphorus": params.phosphorus,
                "potassium": params.potassium,
                "temperature": params.temperature,
                "humidity": params.humidity,
                "soil_ph": params.ph,
                "rainfall": params.rainfall,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )
        
        # Get all crops and calculate compatibility
        crops = list(mongo_db.crop_recommendations.find())
        
        for crop in crops:
            crop.pop('_id', None)
            # Calculate compatibility score
            score = calculate_compatibility(params, crop)
            crop["soil_compatibility"] = score
        
        # Sort by compatibility
        crops.sort(key=lambda x: x["soil_compatibility"], reverse=True)
        
        return {"recommendations": crops[:10]}
    except Exception as e:
        print(f"Get recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_compatibility(params: SoilParams, crop: dict) -> int:
    """Calculate crop compatibility score based on soil parameters"""
    try:
        optimal = crop.get("optimal_conditions", {})
        
        # If no optimal conditions, return default score
        if not optimal:
            return 50
        
        score = 0
        checks = 0
        
        # Temperature check (15 points)
        if "temperature_min" in optimal and "temperature_max" in optimal:
            temp_min, temp_max = optimal["temperature_min"], optimal["temperature_max"]
            if temp_min <= params.temperature <= temp_max:
                score += 15
            elif abs(params.temperature - (temp_min + temp_max) / 2) <= 5:
                score += 10  # Partial score if close
            checks += 15
        
        # Humidity check (15 points)
        if "humidity_min" in optimal and "humidity_max" in optimal:
            hum_min, hum_max = optimal["humidity_min"], optimal["humidity_max"]
            if hum_min <= params.humidity <= hum_max:
                score += 15
            elif abs(params.humidity - (hum_min + hum_max) / 2) <= 10:
                score += 10
            checks += 15
        
        # Rainfall check (15 points)
        if "rainfall_min" in optimal and "rainfall_max" in optimal:
            rain_min, rain_max = optimal["rainfall_min"], optimal["rainfall_max"]
            if rain_min <= params.rainfall <= rain_max:
                score += 15
            elif abs(params.rainfall - (rain_min + rain_max) / 2) <= 20:
                score += 10
            checks += 15
        
        # Nitrogen check (15 points)
        if "nitrogen_min" in optimal and "nitrogen_max" in optimal:
            n_min, n_max = optimal["nitrogen_min"], optimal["nitrogen_max"]
            if n_min <= params.nitrogen <= n_max:
                score += 15
            elif abs(params.nitrogen - (n_min + n_max) / 2) <= 10:
                score += 10
            checks += 15
        
        # Phosphorus check (15 points)
        if "phosphorus_min" in optimal and "phosphorus_max" in optimal:
            p_min, p_max = optimal["phosphorus_min"], optimal["phosphorus_max"]
            if p_min <= params.phosphorus <= p_max:
                score += 15
            elif abs(params.phosphorus - (p_min + p_max) / 2) <= 10:
                score += 10
            checks += 15
        
        # Potassium check (15 points)
        if "potassium_min" in optimal and "potassium_max" in optimal:
            k_min, k_max = optimal["potassium_min"], optimal["potassium_max"]
            if k_min <= params.potassium <= k_max:
                score += 15
            elif abs(params.potassium - (k_min + k_max) / 2) <= 10:
                score += 10
            checks += 15
        
        # pH check (10 points)
        if "ph_min" in optimal and "ph_max" in optimal:
            ph_min, ph_max = optimal["ph_min"], optimal["ph_max"]
            if ph_min <= params.ph <= ph_max:
                score += 10
            elif abs(params.ph - (ph_min + ph_max) / 2) <= 0.5:
                score += 7
            checks += 10
        
        return int((score / checks) * 100) if checks > 0 else 50
    except Exception as e:
        print(f"Compatibility calculation error: {e}")
        return 50

# --- Hindsight Long-Term Memory Foundation (Phase 1 & Phase 2) ---

@app.get("/api/memory/health")
async def memory_health():
    """Hindsight memory foundation health check."""
    service = get_memory_service()
    return service.health_check()

@app.post("/api/memory/retain")
async def memory_retain(request: MemoryRetainRequest, current_user: dict = Depends(get_current_user)):
    """Retain durable farmer memory (enforces authenticated farmer identity)."""
    service = get_memory_service()
    farmer_id = current_user.get("phone_number", "unknown")
    result = service.retain_memory(
        farmer_id=farmer_id,
        memory_type=request.memory_type,
        content=request.content,
        metadata=request.metadata,
        source=request.source or "farmer",
        crop=request.crop,
        location=request.location or current_user.get("location"),
        season=request.season,
        confidence=request.confidence or 1.0,
    )
    return result

@app.post("/api/memory/recall")
async def memory_recall(request: MemoryRecallRequest, current_user: dict = Depends(get_current_user)):
    """Recall memories strictly isolated to the authenticated farmer."""
    service = get_memory_service()
    farmer_id = current_user.get("phone_number", "unknown")
    results = service.recall_memories(
        farmer_id=farmer_id,
        query=request.query,
        memory_types=request.memory_types,
        limit=request.limit or 10,
    )
    return {"farmer_id": farmer_id, "memories": results, "count": len(results)}

@app.get("/api/memory/summary")
async def memory_summary(current_user: dict = Depends(get_current_user)):
    """Get structured long-term memory overview for authenticated farmer."""
    service = get_memory_service()
    farmer_id = current_user.get("phone_number", "unknown")
    return service.get_farmer_memory_summary(farmer_id)

@app.post("/api/recommendation")
async def get_memory_aware_recommendation(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Phase 3: Direct Memory-Aware Recommendation endpoint.
    Recalls isolated farmer memories, filters via precedence policy,
    incorporates existing agricultural context, and returns recommendation
    with structured memory influence metadata.
    """
    farmer_id = current_user.get("phone_number", "unknown")
    user_location = request.location or current_user.get("location", "India")
    recommender = get_recommender()

    # Phase 3: Targeted Memory Retrieval & Assembly
    assembled_context = {}
    raw_memories = []
    memory_prompt_section = ""
    try:
        assembled_context, raw_memories = recommender.assemble_memory_context(
            farmer_id=farmer_id,
            query=request.query,
            location=user_location,
        )
        memory_prompt_section = recommender.format_memory_for_prompt(assembled_context)
    except Exception as recall_err:
        print(f"Hindsight recall error (fallback to standard context): {recall_err}")

    # Fetch agricultural domain context
    context_data = fetch_context_sync(user_location, request.query)
    formatted_context = format_context_for_llm(context_data)

    system_prompt = f"""You are Sarthi, AI agricultural expert for rural India.
Use the current agricultural data and remembered farmer context below to answer.

{formatted_context}
{memory_prompt_section}

Provide actionable, practical, and highly personalized advice."""

    recommendation_id = str(uuid.uuid4())

    try:
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query}
            ],
            max_tokens=600,
            temperature=0.7
        )
        response_text = response.choices[0].message.content
    except Exception as llm_err:
        print(f"LLM execution error: {llm_err}")
        response_text = "Based on current regional weather and soil conditions, select crops suited for your local climate."

    memory_influence = recommender.build_memory_influence_metadata(assembled_context, response_text)
    used_types = list({m.get("type", "profile") for m in raw_memories}) if raw_memories else []
    relevant_memories = []
    for cat, items in assembled_context.items():
        for item in items:
            relevant_memories.append({
                "id": item.get("id"),
                "category": cat,
                "type": item.get("type", cat),
                "summary": item.get("text"),
                "crop": item.get("crop"),
            })

    return {
        "recommendation_id": recommendation_id,
        "farmer_id": farmer_id,
        "query": request.query,
        "recommendation": response_text,
        "memory_context": {
            "used": bool(raw_memories),
            "memory_count": len(raw_memories),
            "types": used_types
        },
        "relevant_memories": relevant_memories,
        "memory_influence": memory_influence,
        "assembled_context": assembled_context
    }


@app.post("/api/memory/compare")
async def compare_recommendation_memory(
    request: MemoryCompareRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Phase 6: Live Comparison Endpoint.
    Runs the recommendation BOTH without memory and with memory using real Azure OpenAI
    and real Hindsight Cloud recall, proving that long-term memory changes the decision.
    """
    farmer_id = current_user.get("phone_number", "unknown")
    user_location = request.location or current_user.get("location", "India")
    recommender = get_recommender()

    # 1. Domain agricultural context (identical for both)
    context_data = fetch_context_sync(user_location, request.query)
    formatted_context = format_context_for_llm(context_data)

    # 2. RUN A: WITHOUT MEMORY
    prompt_without = f"""You are Sarthi, AI agricultural advisor for rural India.
Use current regional environmental data below to advise the farmer.
Provide generic regional agricultural advice based solely on weather, soil, and climate.

{formatted_context}

Be concise and practical."""
    try:
        resp_without = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": prompt_without},
                {"role": "user", "content": request.query}
            ],
            max_tokens=400,
            temperature=0.7
        )
        text_without = resp_without.choices[0].message.content
    except Exception as e:
        text_without = "Standard regional advisory: Cultivate staple seasonal crops suited to regional rainfall and temperature."

    # 3. RUN B: WITH REAL HINDSIGHT MEMORY
    assembled_context = {}
    raw_memories = []
    memory_prompt_section = ""
    try:
        assembled_context, raw_memories = recommender.assemble_memory_context(
            farmer_id=farmer_id,
            query=request.query,
            location=user_location,
        )
        memory_prompt_section = recommender.format_memory_for_prompt(assembled_context)
    except Exception as recall_err:
        print(f"Hindsight recall error in compare: {recall_err}")

    prompt_with = f"""You are Sarthi, AI agricultural advisor for rural India.
Use current regional environmental data and remembered farmer context below to advise the farmer.
CRITICAL: You MUST strictly adapt your advice to respect the historical farmer memories, water limitations, and previous crop outcomes.

{formatted_context}
{memory_prompt_section}

Provide personalized, practical advice addressing their specific farm situation."""

    try:
        resp_with = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": prompt_with},
                {"role": "user", "content": request.query}
            ],
            max_tokens=400,
            temperature=0.7
        )
        text_with = resp_with.choices[0].message.content
    except Exception as e:
        text_with = text_without

    memory_influence = recommender.build_memory_influence_metadata(assembled_context, text_with)
    relevant_memories = []
    for cat, items in assembled_context.items():
        for item in items:
            relevant_memories.append({
                "id": item.get("id"),
                "category": cat,
                "type": item.get("type", cat),
                "summary": item.get("text"),
                "crop": item.get("crop"),
            })

    return {
        "farmer_id": farmer_id,
        "query": request.query,
        "location": user_location,
        "without_memory": {
            "recommendation": text_without,
            "type": "Standard Regional Advisory",
            "memories_used": 0,
            "description": "Computed strictly from regional weather, soil, and crop data with zero farmer memory."
        },
        "with_memory": {
            "recommendation": text_with,
            "type": "Personalized Memory-Aware Advisory",
            "memories_used": len(raw_memories),
            "relevant_memories": relevant_memories,
            "memory_influence": memory_influence,
            "description": "Adapted to historical farmer constraints, past crop failures, and stated preferences retrieved from Hindsight Cloud."
        }
    }


@app.post("/api/memory/demo/reset")
async def reset_demo_farmer_memory(current_user: dict = Depends(get_current_user)):
    """
    Phase 6: Reset mechanism for ONLY the designated demo farmer account (+919999999001).
    Strictly forbidden for all other farmers to guarantee data isolation.
    """
    farmer_id = current_user.get("phone_number", "unknown")
    allowed = {"+919999999001", "demo_farmer", "test_farmer_001"}
    if farmer_id not in allowed:
        raise HTTPException(
            status_code=403,
            detail="Reset is strictly restricted to designated demo accounts to prevent data loss."
        )

    service = get_memory_service()
    try:
        result = service.reset_demo_farmer_memories(farmer_id)
        return result
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset demo memory: {str(e)}")



