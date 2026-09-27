import os
import time
import uuid
import tempfile
import subprocess
from typing import Optional
from fastapi import HTTPException

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    speechsdk = None
    AZURE_SPEECH_AVAILABLE = False

try:
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    AzureOpenAI = None
    OPENAI_AVAILABLE = False

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    boto3 = None
    BOTO3_AVAILABLE = False


class TranscribeService:
    def __init__(self):
        self.azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.azure_speech_region = os.getenv("AZURE_SPEECH_REGION", "centralindia")
        
        self.whisper_key = os.getenv("WHISPER_API_KEY")
        self.whisper_endpoint = os.getenv("WHISPER_ENDPOINT")
        self.whisper_deployment = os.getenv("WHISPER_DEPLOYMENT", "whisper")
        self.whisper_api_version = os.getenv("WHISPER_API_VERSION", "2024-06-01")
        
        self.whisper_client = None
        if OPENAI_AVAILABLE and self.whisper_key and self.whisper_endpoint:
            try:
                self.whisper_client = AzureOpenAI(
                    azure_endpoint=self.whisper_endpoint,
                    api_key=self.whisper_key,
                    api_version=self.whisper_api_version
                )
            except Exception as e:
                print(f"Whisper client init failed: {e}")

        self.bucket_name = os.getenv("AWS_S3_BUCKET")
        self.s3_client = None
        self.transcribe_client = None
        if BOTO3_AVAILABLE and self.bucket_name:
            try:
                self.s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-south-1"))
                self.transcribe_client = boto3.client("transcribe", region_name=os.getenv("AWS_REGION", "ap-south-1"))
            except Exception as e:
                print(f"AWS Transcribe init failed: {e}")

    def _convert_to_16k_wav(self, audio_bytes: bytes, file_extension: str) -> str:
        """Convert input audio bytes to 16kHz mono WAV file using ffmpeg if available"""
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as in_f:
            in_f.write(audio_bytes)
            in_path = in_f.name

        out_path = in_path + ".16k.wav"
        ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"

        try:
            cmd = [ffmpeg_bin, "-y", "-i", in_path, "-ac", "1", "-ar", "16000", out_path]
            res = subprocess.run(cmd, capture_output=True)
            if res.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                return out_path
        except Exception as e:
            print(f"FFmpeg conversion error: {e}")
        finally:
            if os.path.exists(in_path):
                try:
                    os.remove(in_path)
                except Exception:
                    pass

        # Return original written file if ffmpeg failed
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fallback_f:
            fallback_f.write(audio_bytes)
            return fallback_f.name

    def transcribe_azure_speech(self, wav_path: str, language: str = "hi") -> Optional[str]:
        """Transcribe audio using Azure Speech Services SDK"""
        if not (AZURE_SPEECH_AVAILABLE and self.azure_speech_key and self.azure_speech_region):
            return None

        language_map = {
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
        speech_lang = language_map.get(language, "hi-IN")

        try:
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_speech_key,
                region=self.azure_speech_region
            )
            speech_config.speech_recognition_language = speech_lang
            audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
            result = recognizer.recognize_once_async().get()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech and result.text.strip():
                return result.text.strip()
            print(f"Azure speech recognition non-match: {result.reason}")
        except Exception as e:
            print(f"Azure Speech recognition error: {e}")

        return None

    def transcribe_whisper(self, wav_path: str, language: str = "hi") -> Optional[str]:
        """Transcribe audio using Azure OpenAI Whisper"""
        if not self.whisper_client:
            return None

        try:
            with open(wav_path, "rb") as audio_file:
                transcript_obj = self.whisper_client.audio.transcriptions.create(
                    model=self.whisper_deployment,
                    file=audio_file,
                    language=language if language in ["hi", "te", "en", "ta", "mr", "gu", "kn", "ml", "bn"] else None
                )
                if transcript_obj and transcript_obj.text:
                    return transcript_obj.text.strip()
        except Exception as e:
            print(f"Whisper transcription error: {e}")

        return None

    def transcribe_aws(self, file_bytes: bytes, file_extension: str, language: str = "hi") -> Optional[str]:
        """Fallback to AWS Transcribe if configured"""
        if not (self.s3_client and self.transcribe_client and self.bucket_name):
            return None

        language_map = {
            "en": "en-IN",
            "hi": "hi-IN",
            "ta": "ta-IN",
            "te": "te-IN",
            "kn": "kn-IN",
            "ml": "ml-IN",
            "bn": "bn-IN",
            "gu": "gu-IN",
            "mr": "mr-IN"
        }
        language_code = language_map.get(language, "hi-IN")
        job_name = f"transcribe-{uuid.uuid4()}"
        file_key = f"transcribe/{uuid.uuid4()}.{file_extension}"

        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=file_key, Body=file_bytes)
            s3_uri = f"s3://{self.bucket_name}/{file_key}"
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": s3_uri},
                MediaFormat=file_extension if file_extension in ["wav", "mp3", "ogg"] else "wav",
                LanguageCode=language_code
            )

            start_time = time.time()
            while time.time() - start_time < 30:
                res = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
                status = res["TranscriptionJob"]["TranscriptionJobStatus"]
                if status == "COMPLETED":
                    transcript_uri = res["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                    import requests
                    transcript_data = requests.get(transcript_uri).json()
                    return transcript_data["results"]["transcripts"][0]["transcript"]
                elif status == "FAILED":
                    break
                time.sleep(2)
        except Exception as e:
            print(f"AWS Transcribe error: {e}")
        finally:
            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            except Exception:
                pass

        return None

    async def transcribe_audio(self, file_bytes: bytes, file_extension: str, language: str = "hi") -> str:
        """Complete resilient transcription workflow across Azure Speech, Whisper, and AWS"""
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty audio recording received")

        wav_path = self._convert_to_16k_wav(file_bytes, file_extension)

        try:
            # 1. Try Azure Speech SDK (fastest, optimized for Indian languages)
            transcript = self.transcribe_azure_speech(wav_path, language)
            if transcript:
                return transcript

            # 2. Try Azure OpenAI Whisper
            transcript = self.transcribe_whisper(wav_path, language)
            if transcript:
                return transcript

            # 3. Try AWS Transcribe
            transcript = self.transcribe_aws(file_bytes, file_extension, language)
            if transcript:
                return transcript

            raise HTTPException(status_code=400, detail="Could not recognize speech from audio. Please speak clearly or try typing.")
        finally:
            if os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass
