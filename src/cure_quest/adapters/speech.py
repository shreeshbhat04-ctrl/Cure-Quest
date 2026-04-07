import logging

from google.cloud import speech
from google.cloud import texttospeech

from cure_quest.config import get_settings

logger = logging.getLogger(__name__)

class GoogleSpeechAdapter:
    """Adapter for Google Cloud Speech-to-Text and Text-to-Speech API."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str | None = None) -> str:
        """Transcribe audio bytes using Google Cloud STT.
        
        It attempts to auto-detect the encoding (e.g. WebM/Opus from browsers) 
        and extract the transcript string.
        """
        # Instantiate the client using Google Cloud Application Default Credentials (ADC)
        # This prevents it from failing when expecting 'refresh_token' from workspace scopes.
        client = speech.SpeechClient()

        audio = speech.RecognitionAudio(content=audio_bytes)
        
        # Configure for common browser WebM/Ogg audio uploads
        # We rely on google-cloud-speech's ability to auto-detect WebM/Opus if headers match
        # WEBM_OPUS is the standard output of MediaRecorder across modern browsers
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )

        try:
            response = client.recognize(config=config, audio=audio)
            
            transcript_parts = []
            for result in response.results:
                transcript_parts.append(result.alternatives[0].transcript)
                
            full_transcript = " ".join(transcript_parts).strip()
            if not full_transcript:
                logger.warning("Google STT returned an empty transcript.")
            
            return full_transcript

        except Exception as e:
            logger.error("Speech to Text failed: %s", e)
            # Depending on platform, browsers might use different encodings like MP4 or LINEAR16,
            # If WebM/Opus fails, try letting Google auto-detect (works for FLAC, WAV, some others)
            logger.info("Attempting auto-detect fallback recognition...")
            fallback_config = speech.RecognitionConfig(
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            fallback_response = client.recognize(config=fallback_config, audio=audio)
            
            transcript_parts = []
            for result in fallback_response.results:
                transcript_parts.append(result.alternatives[0].transcript)
                
            return " ".join(transcript_parts).strip()

    def synthesize_speech(self, text: str) -> bytes:
        """Synthesize text into speech using Google Cloud TTS."""
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-F", # Premium Journey voice
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content
