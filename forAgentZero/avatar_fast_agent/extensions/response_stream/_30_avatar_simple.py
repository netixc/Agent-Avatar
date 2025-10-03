"""
Avatar Simple Extension - Simplified version for stability

Sends complete Agent-Zero responses to Avatar without duplicates.
"""

from python.helpers.extension import Extension
from agent import LoopData
import requests
import base64
import re
import time
import asyncio
from openai import OpenAI
import wave
import io
import os


class AvatarSimple(Extension):
    """Simple Avatar integration that just works"""

    # Class-level tracking to persist across instances
    _sent_messages = set()
    _last_clear_time = time.time()
    _pending_response = ""
    _last_update_time = 0
    _send_task = None
    _last_sent_length = 0  # Track how much we've already sent
    _sent_sentence_hashes = set()  # Track which sentences we've sent

    # Configuration - will be loaded from agent config and Avatar API
    AVATAR_API_URL = None
    TTS_BASE_URL = None
    TTS_VOICE = None
    TTS_MODEL = None
    _config_loaded = False

    def __init__(self, agent):
        super().__init__(agent)
        # Load Avatar API URL from agent config on first init
        if not AvatarSimple._config_loaded:
            self._load_avatar_url_from_agent_config()
            self._load_config_from_avatar()

    def _load_avatar_url_from_agent_config(self):
        """Load Avatar API URL from agent's config file"""
        import yaml
        from python.helpers import files

        config_file = "avatar_config.yaml"
        config_path = files.get_abs_path(f"agents/{self.agent.config.profile}/{config_file}")

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                AvatarSimple.AVATAR_API_URL = config.get("avatar_api_url")
                if not AvatarSimple.AVATAR_API_URL:
                    raise ValueError(f"avatar_api_url not found in {config_path}")
            else:
                # Try environment variable
                AvatarSimple.AVATAR_API_URL = os.getenv("AVATAR_API_URL")
                if not AvatarSimple.AVATAR_API_URL:
                    raise FileNotFoundError(f"Config file not found: {config_path} and AVATAR_API_URL env var not set")
        except Exception as e:
            self.agent.context.log.log(
                type="error",
                heading="Avatar Config",
                content=f"Failed to load Avatar API URL: {e}"
            )
            raise

    def _load_config_from_avatar(self):
        """Load TTS configuration from Avatar API"""
        try:
            response = requests.get(
                f"{self.AVATAR_API_URL}/api/config",
                timeout=5
            )
            if response.status_code == 200:
                config = response.json()
                AvatarSimple.TTS_BASE_URL = config.get("tts", {}).get("base_url")
                AvatarSimple.TTS_VOICE = config.get("tts", {}).get("voice")
                AvatarSimple.TTS_MODEL = config.get("tts", {}).get("model")
                AvatarSimple._config_loaded = True
                self.agent.context.log.log(
                    type="info",
                    heading="Avatar Config",
                    content=f"Loaded config from Avatar: TTS={self.TTS_BASE_URL}, Voice={self.TTS_VOICE}, Model={self.TTS_MODEL}"
                )
            else:
                raise Exception(f"API returned {response.status_code}")
        except Exception as e:
            self.agent.context.log.log(
                type="error",
                heading="Avatar Config",
                content=f"Failed to load config from Avatar API: {str(e)}"
            )
            raise

    async def execute(self, loop_data=None, text="", parsed=None, **kwargs):
        """Process streaming response text in real-time"""
        # Skip if not a response tool
        if (
            not parsed
            or not isinstance(parsed, dict)
            or parsed.get("tool_name") != "response"
            or "tool_args" not in parsed
            or "text" not in parsed["tool_args"]
            or not parsed["tool_args"]["text"]
        ):
            return

        # Get the current streaming response text
        response_text = parsed["tool_args"]["text"].strip()
        if not response_text:
            return

        # Reset tracking if this is a completely new response
        if not AvatarSimple._pending_response or not response_text.startswith(AvatarSimple._pending_response):
            AvatarSimple._last_sent_length = 0
            AvatarSimple._sent_sentence_hashes.clear()

        # Update pending response
        AvatarSimple._pending_response = response_text

        # Process any new complete sentences immediately
        await self._process_new_sentences(response_text)

    async def _process_new_sentences(self, full_text):
        """Process any new complete sentences in the streaming text"""
        try:
            # Extract all complete sentences from the FULL text
            sentences = self._extract_all_complete_sentences(full_text)

            for sentence in sentences:
                sentence_stripped = sentence.strip()
                if not sentence_stripped:
                    continue

                # Use hash to track if we've sent this exact sentence before
                sentence_hash = hash(sentence_stripped)
                if sentence_hash in AvatarSimple._sent_sentence_hashes:
                    continue

                # Sentence already has emotion tag - send directly without adding emotion
                await self._send_single_emotion_direct(sentence_stripped)

                # Mark as sent
                AvatarSimple._sent_sentence_hashes.add(sentence_hash)

        except Exception as e:
            # Don't interrupt streaming on errors
            pass

    async def _send_single_emotion_direct(self, text_with_emotion):
        """Send text that already includes emotion tag to Avatar"""
        try:
            # Generate audio (this will strip emotion tags for TTS)
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_audio, text_with_emotion
            )
            if not audio_data:
                return

            # Simple volume pattern
            duration_ms = len(audio_data) // 88
            num_chunks = max(1, duration_ms // 20)
            volumes = [0.7] * num_chunks

            # Extract emotion and motion tags, keep original text with all tags for Avatar
            # Avatar backend will extract both emotions and motions from the text
            # The frontend will strip them for display
            payload = {
                "type": "external_audio",
                "audio": base64.b64encode(audio_data).decode('utf-8'),
                "volumes": volumes,
                "slice_length": 20,
                "display_text": {
                    "text": text_with_emotion,  # Keep original with ALL tags (emotions + motions)
                    "display_clean": True,  # Signal to frontend: strip emotion and motion tags
                    "duration": len(volumes) * 0.02
                },
                "source": "agent_zero_streaming"
            }

            response = requests.post(
                f"{self.AVATAR_API_URL}/api/external_audio",
                json=payload,
                timeout=5
            )

        except Exception as e:
            # Don't interrupt streaming on errors
            pass

    async def _send_single_emotion_async(self, emotion, text):
        """Send a single emotion and text to Avatar asynchronously"""
        try:
            # Generate audio in background
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_audio, text
            )
            if not audio_data:
                return

            # Simple volume pattern
            duration_ms = len(audio_data) // 88
            num_chunks = max(1, duration_ms // 20)
            volumes = [0.7] * num_chunks

            # Send to Avatar
            payload = {
                "type": "external_audio",
                "audio": base64.b64encode(audio_data).decode('utf-8'),
                "volumes": volumes,
                "slice_length": 20,
                "display_text": {
                    "text": f"{emotion} {text}",
                    "duration": len(volumes) * 0.02
                },
                "source": "agent_zero_streaming"
            }

            response = requests.post(
                f"{self.AVATAR_API_URL}/api/external_audio",
                json=payload,
                timeout=5
            )

        except Exception as e:
            # Don't interrupt streaming on errors
            pass

    def _extract_all_complete_sentences(self, text):
        """Extract all complete emotion-tagged and motion-tagged sentences from text"""
        import re
        sentences = []

        # Split text by emotion/motion tags to get segments
        # Pattern captures emotion tags [joy] and motion tags {wave}
        segments = re.split(r'(\[(?:joy|sadness|anger|fear|neutral|surprise|smirk|disgust)\]|\{(?:nod|wave|angry|sad|surprised|sneeze)\})', text, flags=re.IGNORECASE)

        current_tags = ""  # Track accumulated emotion/motion tags
        for i, segment in enumerate(segments):
            segment = segment.strip()
            if not segment:
                continue

            # Check if this is an emotion or motion tag
            if re.match(r'\[(?:joy|sadness|anger|fear|neutral|surprise|smirk|disgust)\]|\{(?:nod|wave|angry|sad|surprised|sneeze)\}', segment, re.IGNORECASE):
                current_tags += f"{segment} "
            else:
                # This is text content
                if segment:
                    # Split this segment into sentences
                    # Find all sentences ending with punctuation
                    sentence_pattern = r'[^.!?]*[.!?]+'
                    for match in re.finditer(sentence_pattern, segment):
                        sentence_text = match.group().strip()
                        if sentence_text:
                            # Combine all tags with sentence
                            full_sentence = f"{current_tags}{sentence_text}".strip()
                            sentences.append(full_sentence)
                    # Reset tags after using them
                    current_tags = ""

        return sentences

    def _extract_complete_sentences(self, text):
        """Legacy method - extract sentences without emotion tags"""
        import re
        sentences = []
        current_pos = 0

        # Find sentence endings with punctuation
        for match in re.finditer(r'[.!?]+\s*', text):
            sentence = text[current_pos:match.end()].strip()
            if sentence:
                sentences.append(sentence)
            current_pos = match.end()

        return sentences

    def _looks_complete(self, text):
        """Check if response looks complete (ends with punctuation)"""
        return text.strip().endswith(('.', '!', '?', '😊', '😢', '😠', '😮', '😎', '🤔', '🤖'))

    async def _send_to_avatar(self, response_text):
        """Actually send the response to Avatar"""
        try:
            # Get emotion for the whole response
            emotion = self._get_emotion(response_text)

            # Send the complete response with detected emotion
            await self._send_single_emotion(emotion, response_text)

        except Exception as e:
            if str(e).strip():
                self.agent.context.log.log(
                    type="error",
                    heading="Avatar Error",
                    content=f"Send error: {str(e)[:100]}"
                )

    async def _send_single_emotion(self, emotion, text):
        """Send a single emotion and text to VTube"""
        try:
            text_with_emotion = f"{emotion} {text}"

            # Generate audio
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_audio, text
            )
            if not audio_data:
                return

            # Simple volume pattern like old extension - faster
            duration_ms = len(audio_data) // 88  # Rough estimate
            num_chunks = max(1, duration_ms // 20)
            volumes = [0.7] * num_chunks

            # Send to Avatar
            payload = {
                "type": "external_audio",
                "audio": base64.b64encode(audio_data).decode('utf-8'),
                "volumes": volumes,
                "slice_length": 20,
                "display_text": {
                    "text": text_with_emotion,
                    "duration": len(volumes) * 0.02
                },
                "source": "agent_zero_extension"
            }

            response = requests.post(
                f"{self.AVATAR_API_URL}/api/external_audio",
                json=payload,
                timeout=5
            )

            if response.status_code != 200:
                self.agent.context.log.log(
                    type="error",
                    heading="Avatar Error",
                    content=f"API returned {response.status_code}"
                )

        except Exception as e:
            if str(e).strip():
                self.agent.context.log.log(
                    type="error",
                    heading="Avatar Error",
                    content=f"Send error: {str(e)[:100]}"
                )

    def _get_emotion(self, text):
        """Enhanced emotion detection supporting all Avatar model emotions"""
        text_lower = text.lower()

        # Check if emotion tag already exists in text
        emotion_tags = re.findall(r'\[(\w+)\]', text)
        if emotion_tags:
            # Return the first emotion tag found
            return f"[{emotion_tags[0]}]"

        # When user asks to show faces/emotions, show joy as default
        if "faces" in text_lower and "make" in text_lower:
            return "[joy]"

        # Map emojis to emotions - comprehensive mapping
        emoji_emotion_map = {
            "😀": "[joy]", "😊": "[joy]", "😃": "[joy]", "😄": "[joy]", "😁": "[joy]", "😍": "[joy]", "🥰": "[joy]",
            "😢": "[sadness]", "😞": "[sadness]", "😔": "[sadness]", "😭": "[sadness]",
            "😠": "[anger]", "😡": "[anger]", "🤬": "[anger]",
            "😲": "[surprise]", "😮": "[surprise]", "😯": "[surprise]",
            "😨": "[fear]", "😰": "[fear]", "😱": "[fear]",
            "😉": "[smirk]", "😏": "[smirk]", "😎": "[smirk]",
            "🤔": "[smirk]",  # Thinking maps to smirk
            "🤖": "[neutral]",  # Robot maps to neutral
            "😕": "[neutral]", "😐": "[neutral]"
        }

        # Check for the FIRST emoji and map to emotion (prioritizes first emoji in response)
        for emoji, emotion in emoji_emotion_map.items():
            if emoji in text:
                return emotion  # Direct mapping - simpler and faster

        # Check for emotional content in the response (without explicit face request)
        if any(w in text_lower for w in ["hello", "hi", "great", "wonderful", "awesome", "fantastic"]):
            return "[joy]"
        elif any(w in text_lower for w in ["sorry", "unfortunately", "regret"]):
            return "[sadness]"
        elif any(w in text_lower for w in ["error", "wrong", "failed", "frustrated", "annoying"]):
            return "[anger]"
        elif any(w in text_lower for w in ["wow", "amazing", "incredible", "unbelievable"]):
            return "[surprise]"
        elif any(w in text_lower for w in ["scared", "afraid", "terrified"]):
            return "[fear]"
        elif any(w in text_lower for w in ["hmm", "thinking", "perhaps", "maybe", "consider"]):
            return "[smirk]"
        elif any(w in text_lower for w in ["gross", "disgusting", "ugh", "yuck"]):
            return "[disgust]"
        else:
            return "[neutral]"

    def _calculate_volumes(self, audio_data):
        """Calculate realistic volume levels for lip-sync"""
        try:
            # Parse WAV header to get duration
            audio_file = io.BytesIO(audio_data)
            with wave.open(audio_file, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration_ms = (frames / rate) * 1000

            # Calculate number of 20ms chunks
            chunk_count = int(duration_ms / 20)

            # Create a varying volume pattern for realistic lip-sync
            volumes = []
            for i in range(chunk_count):
                # Create natural speech pattern with variation
                base = 0.5
                variation = 0.3 * abs((i % 10) - 5) / 5  # Wave pattern
                noise = 0.1 * (i % 3) / 3  # Small noise
                volume = min(1.0, base + variation + noise)
                volumes.append(volume)

            return volumes if volumes else [0.5]

        except Exception as e:
            # Fallback to simple pattern
            duration_estimate = len(audio_data) // 88
            chunk_count = max(1, duration_estimate // 20)
            return [0.5 + 0.2 * (i % 2) for i in range(chunk_count)]

    def _generate_audio(self, text):
        """Generate audio with Kokoro TTS"""
        try:
            # Clean text for TTS - remove emojis, markdown, and emotion tags
            clean_text = self._clean_text_for_tts(text)

            client = OpenAI(
                api_key="not-needed",
                base_url=self.TTS_BASE_URL
            )

            response = client.audio.speech.create(
                model=self.TTS_MODEL,
                voice=self.TTS_VOICE,
                response_format="wav",
                input=clean_text
            )

            return response.content

        except Exception as e:
            self.agent.context.log.log(
                type="error",
                heading="TTS Error",
                content=f"Failed to generate audio: {str(e)[:100]}"
            )
            return None

    def _clean_text_for_tts(self, text):
        """Remove emotion tags, motion tags, emojis, markdown, and clean text for TTS"""
        import re

        # IMPORTANT: Remove emotion tags first (e.g., [joy], [sadness], etc.)
        clean = re.sub(r'\[\w+\]', '', text)

        # Remove common emojis and their descriptions
        emoji_patterns = [
            r'😊|😃|😄|😁|🙂|🙃|😉',  # Happy emojis
            r'😢|😭|😞|😔|☹️|🙁',      # Sad emojis
            r'😠|😡|😤|🤬',            # Angry emojis
            r'😲|😮|😯|😦|😧|🤯',      # Surprised emojis
            r'😨|😰|😱',              # Fear emojis
            r'[\U0001F600-\U0001F64F]',  # Emoticons
            r'[\U0001F300-\U0001F5FF]',  # Symbols & pictographs
        ]

        for pattern in emoji_patterns:
            clean = re.sub(pattern, '', clean)

        # Remove markdown formatting
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', clean)  # Bold
        clean = re.sub(r'\*(.+?)\*', r'\1', clean)      # Italic
        clean = re.sub(r'`(.+?)`', r'\1', clean)        # Code

        # Remove "Face:" patterns when followed by nothing or just whitespace
        clean = re.sub(r'(Happy|Sad|Angry|Fear|Surprised?)\s*Face:\s*,\s*', '', clean, flags=re.MULTILINE)
        clean = re.sub(r'(Happy|Sad|Angry|Fear|Surprised?)\s*Face:\s*(?=\n|$)', '', clean)

        # Remove extra whitespace
        clean = ' '.join(clean.split())

        return clean.strip()