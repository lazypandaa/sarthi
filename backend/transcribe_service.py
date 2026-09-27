import boto3
import time
import uuid
import os
from typing import Optional
from fastapi import HTTPException

class TranscribeService:
    def __init__(self):
        self.s3_client = boto3.client("s3", region_name="ap-south-1")
        self.transcribe_client = boto3.client("transcribe", region_name="ap-south-1")
        self.bucket_name = os.getenv("AWS_S3_BUCKET")
        
        if not self.bucket_name:
            raise ValueError("AWS_S3_BUCKET environment variable not set")
    
    def upload_to_s3(self, file_bytes: bytes, file_extension: str) -> str:
        """Upload audio file to S3 and return the S3 URI"""
        try:
            file_key = f"transcribe/{uuid.uuid4()}.{file_extension}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_bytes
            )
            return f"s3://{self.bucket_name}/{file_key}", file_key
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
    
    def start_transcription_job(self, job_name: str, s3_uri: str, language_code: str = "hi-IN") -> str:
        """Start Amazon Transcribe job"""
        try:
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": s3_uri},
                MediaFormat="wav",
                LanguageCode=language_code
            )
            return job_name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcribe job failed: {str(e)}")
    
    def get_transcription_result(self, job_name: str, max_wait: int = 60) -> str:
        """Poll for transcription result"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                status = response["TranscriptionJob"]["TranscriptionJobStatus"]
                
                if status == "COMPLETED":
                    transcript_uri = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                    import requests
                    transcript_data = requests.get(transcript_uri).json()
                    return transcript_data["results"]["transcripts"][0]["transcript"]
                
                elif status == "FAILED":
                    reason = response["TranscriptionJob"].get("FailureReason", "Unknown")
                    raise HTTPException(status_code=500, detail=f"Transcription failed: {reason}")
                
                time.sleep(2)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error checking job: {str(e)}")
        
        raise HTTPException(status_code=408, detail="Transcription timeout")
    
    def cleanup_s3_file(self, file_key: str):
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
        except Exception as e:
            print(f"S3 cleanup failed: {e}")
    
    async def transcribe_audio(self, file_bytes: bytes, file_extension: str, language: str = "hi") -> str:
        """Complete transcription workflow"""
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
        file_key = None
        
        try:
            s3_uri, file_key = self.upload_to_s3(file_bytes, file_extension)
            self.start_transcription_job(job_name, s3_uri, language_code)
            transcript = self.get_transcription_result(job_name)
            return transcript
        finally:
            if file_key:
                self.cleanup_s3_file(file_key)
