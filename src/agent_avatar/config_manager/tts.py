# config_manager/tts.py
from pydantic import ValidationInfo, Field, model_validator
from typing import Literal, Optional, Dict, ClassVar
from .i18n import I18nMixin, Description























class OpenAITTSConfig(I18nMixin):
    """Configuration for OpenAI TTS and compatible APIs."""

    base_url: str = Field("https://api.openai.com/v1", alias="base_url")
    api_key: str = Field(..., alias="api_key")
    model: str = Field("tts-1", alias="model")
    voice: str = Field("alloy", alias="voice")
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = Field("mp3", alias="response_format")
    speed: float = Field(1.0, alias="speed")
    timeout: int = Field(30, alias="timeout")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "base_url": Description(
            en="Base URL for OpenAI-compatible TTS API", 
            zh="OpenAI 兼容 TTS API 的基础 URL"
        ),
        "api_key": Description(
            en="API key for authentication", 
            zh="用于身份验证的 API 密钥"
        ),
        "model": Description(
            en="TTS model to use (e.g., tts-1, tts-1-hd)", 
            zh="要使用的 TTS 模型（如 tts-1、tts-1-hd）"
        ),
        "voice": Description(
            en="Voice to use (alloy, echo, fable, onyx, nova, shimmer)", 
            zh="要使用的语音（alloy、echo、fable、onyx、nova、shimmer）"
        ),
        "response_format": Description(
            en="Audio format for the response", 
            zh="响应的音频格式"
        ),
        "speed": Description(
            en="Speech speed multiplier (0.25-4.0)", 
            zh="语速倍数（0.25-4.0）"
        ),
        "timeout": Description(
            en="Request timeout in seconds", 
            zh="请求超时时间（秒）"
        ),
    }




class TTSConfig(I18nMixin):
    """Configuration for Text-to-Speech."""

    tts_model: Literal["openai_tts"] = Field(..., alias="tts_model")

    openai_tts: Optional[OpenAITTSConfig] = Field(None, alias="openai_tts")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "tts_model": Description(
            en="Text-to-speech model to use", zh="要使用的文本转语音模型"
        ),
        "openai_tts": Description(
            en="Configuration for OpenAI TTS", zh="OpenAI TTS 配置"
        ),
    }

    @model_validator(mode="after")
    def check_tts_config(cls, values: "TTSConfig", info: ValidationInfo):
        tts_model = values.tts_model

        # Only validate the selected TTS model
        if tts_model == "openai_tts" and values.openai_tts is not None:
            values.openai_tts.model_validate(values.openai_tts.model_dump())

        return values
