# 🌾 Sarthi Android Application

Native Android client for **Sarthi (सारथी)** — AI Voice & Farm Memory Companion for Indian Farmers.

---

## 📱 Project Specifications

- **Package / Namespace**: `ai.sarthi.app`
- **Application Name**: `Sarthi`
- **Language**: Kotlin 2.0
- **Compile SDK**: `35`
- **Target SDK**: `34`
- **Min SDK**: `26` (Android 8.0 Oreo+)
- **Architecture**: Clean MVVM + Repository Pattern
- **Networking**: Retrofit 2 + OkHttp 3 + Coroutines + Gson
- **Voice Pipeline**: Native 16kHz PCM WAV Audio Recording + Base64 Voice Playback (Sarvam Bulbul TTS via backend)

---

## 🏗️ Architecture & Modules

```
android/
├── app/
│   ├── build.gradle.kts
│   ├── proguard-rules.pro
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/ai/sarthi/app/
│       │   ├── SarthiApplication.kt         # Application entry point & DI singleton
│       │   ├── audio/
│       │   │   ├── AudioRecorderManager.kt  # 16kHz Mono WAV recorder for Sarvam STT
│       │   │   └── AudioPlayerManager.kt    # Base64 WAV player for Sarvam Bulbul TTS
│       │   ├── data/
│       │   │   ├── local/
│       │   │   │   └── TokenManager.kt      # Encrypted/secured JWT token & farmer session storage
│       │   │   ├── model/
│       │   │   │   ├── AgriModels.kt        # Crop recommendations, weather, markets, advisories
│       │   │   │   ├── AuthModels.kt        # Login, signup, user profiles
│       │   │   │   ├── MemoryModels.kt      # Hindsight memory summary and teach requests
│       │   │   │   └── VoiceModels.kt       # Voice assistant query/response contracts
│       │   │   └── remote/
│       │   │       ├── AgriDataApi.kt       # Government-grounded agricultural REST endpoints
│       │   │       ├── ApiClient.kt         # Retrofit & OkHttp client with AuthInterceptor
│       │   │       ├── AuthApi.kt           # Authentication & profile endpoints
│       │   │       ├── MemoryApi.kt         # Hindsight long-term memory endpoints
│       │   │       └── VoiceAssistantApi.kt # Multilingual voice & text endpoints
│       │   └── ui/
│       │       └── MainActivity.kt          # Launch activity with live backend health monitor
│       └── res/                             # Sarthi brand resources, layouts, adaptive icons
├── gradle/wrapper/
├── build.gradle.kts
├── settings.gradle.kts
└── gradle.properties
```

---

## 🔒 Security & Voice Integration Policy

1. **No Client-Side API Keys**:
   - The Sarvam AI API key is strictly maintained on the Sarthi FastAPI backend (`https://sarthi-api.azurewebsites.net`).
   - The Android app **never** holds or exposes the Sarvam secret key.
2. **Audio Streaming**:
   - Spoken audio is recorded in 16kHz mono WAV format by `AudioRecorderManager` and sent via `MultipartBody` to `POST /process-audio`.
   - The backend runs Sarvam Saaras STT and returns the transcript, reasoning response, and Sarvam Bulbul TTS audio in base64.
   - `AudioPlayerManager` seamlessly streams and plays the synthesized audio to the farmer.

---

## 🚀 Building & Running

### Using Android Studio
1. Open Android Studio.
2. Select **Open an Existing Project** and choose the `/android` folder.
3. Android Studio will automatically sync Gradle and index the project.
4. Select a connected device or emulator and click **Run**.

### Using Command Line
```bash
cd android
./gradlew assembleDebug
```
The compiled debug APK will be generated at:
`app/build/outputs/apk/debug/app-debug.apk`
