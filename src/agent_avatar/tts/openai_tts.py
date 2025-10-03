import sys
import os
import httpx
import base64
from typing import Optional

from loguru import logger
from .tts_interface import TTSInterface

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


class TTSEngine(TTSInterface):
    """OpenAI TTS API implementation.
    
    This implementation supports OpenAI's TTS API and compatible services.
    It has been tested with:
    - OpenAI official API
    - Kokoro FastAPI
    - Groq TTS API
    - Spark TTS FastAPI
    """

    def __init__(
        self,
        base_url: str = "https://api.openai.com/v1",
        api_key: str = "",
        model: str = "tts-1",
        voice: str = "alloy",
        response_format: str = "mp3",
        speed: float = 1.0,
        timeout: int = 30,
    ):
        """Initialize OpenAI TTS engine.
        
        Args:
            base_url: The base URL for the OpenAI-compatible API
            api_key: API key for authentication
            model: TTS model to use (e.g., "tts-1", "tts-1-hd")
            voice: Voice to use (e.g., "alloy", "echo", "fable", "onyx", "nova", "shimmer")
            response_format: Audio format (mp3, opus, aac, flac, wav, pcm)
            speed: Speech speed (0.25 to 4.0)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.voice = voice
        self.response_format = response_format
        self.speed = speed
        self.timeout = timeout
        
        self.file_extension = response_format if response_format != "pcm" else "raw"
        self.new_audio_dir = "cache"
        
        if not os.path.exists(self.new_audio_dir):
            os.makedirs(self.new_audio_dir)
    
    def generate_audio(self, text: str, file_name_no_ext: Optional[str] = None) -> str:
        """Generate speech audio file using OpenAI TTS API.
        
        Args:
            text: The text to convert to speech
            file_name_no_ext: Optional file name without extension
            
        Returns:
            str: Path to the generated audio file
        """
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        
        try:
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": self.model,
                "input": text,
                "voice": self.voice,
                "response_format": self.response_format,
                "speed": self.speed,
            }
            
            # Make the API request
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/audio/speech",
                    headers=headers,
                    json=data,
                )
                
                if response.status_code != 200:
                    error_msg = f"OpenAI TTS API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                    logger.error(error_msg)
                    return None
                
                # Save the audio file
                with open(file_name, "wb") as f:
                    f.write(response.content)
                
                logger.debug(f"Generated audio file: {file_name}")
                return file_name
                
        except httpx.TimeoutException:
            logger.error(f"OpenAI TTS API request timed out after {self.timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error generating audio with OpenAI TTS: {e}")
            return None
    
    async def async_generate_audio(self, text: str, file_name_no_ext: Optional[str] = None) -> str:
        """Asynchronously generate speech audio file using OpenAI TTS API.
        
        Args:
            text: The text to convert to speech
            file_name_no_ext: Optional file name without extension
            
        Returns:
            str: Path to the generated audio file
        """
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        
        try:
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": self.model,
                "input": text,
                "voice": self.voice,
                "response_format": self.response_format,
                "speed": self.speed,
            }
            
            # Make the async API request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/audio/speech",
                    headers=headers,
                    json=data,
                )
                
                if response.status_code != 200:
                    error_msg = f"OpenAI TTS API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                    logger.error(error_msg)
                    return None
                
                # Save the audio file
                with open(file_name, "wb") as f:
                    f.write(response.content)
                
                logger.debug(f"Generated audio file: {file_name}")
                return file_name
                
        except httpx.TimeoutException:
            logger.error(f"OpenAI TTS API request timed out after {self.timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error generating audio with OpenAI TTS: {e}")
            return None