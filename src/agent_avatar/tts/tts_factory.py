from typing import Type
from .tts_interface import TTSInterface


class TTSFactory:
    @staticmethod
    def get_tts_engine(engine_type, **kwargs) -> Type[TTSInterface]:
        if engine_type == "openai_tts":
            from .openai_tts import TTSEngine as OpenAITTSEngine

            return OpenAITTSEngine(
                base_url=kwargs.get("base_url", "https://api.openai.com/v1"),
                api_key=kwargs.get("api_key"),
                model=kwargs.get("model", "tts-1"),
                voice=kwargs.get("voice", "alloy"),
                response_format=kwargs.get("response_format", "mp3"),
                speed=kwargs.get("speed", 1.0),
                timeout=kwargs.get("timeout", 30),
            )

        else:
            raise ValueError(f"Unknown TTS engine type: {engine_type}")


# Example usage:
# tts_engine = TTSFactory.get_tts_engine("openai_tts", api_key="your_api_key", model="tts-1", voice="alloy")
# tts_engine.generate_audio("Hello world")
