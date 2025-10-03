# config_manager/asr.py
from pydantic import ValidationInfo, Field, model_validator
from typing import Literal, Optional, Dict, ClassVar
from .i18n import I18nMixin, Description


class FasterWhisperConfig(I18nMixin):
    """Configuration for Faster Whisper ASR."""

    model_path: str = Field(..., alias="model_path")
    download_root: str = Field(..., alias="download_root")
    language: Optional[str] = Field(None, alias="language")
    device: Literal["auto", "cpu", "cuda"] = Field("auto", alias="device")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "model_path": Description(
            en="Path to the Faster Whisper model", zh="Faster Whisper 模型路径"
        ),
        "download_root": Description(
            en="Root directory for downloading models", zh="模型下载根目录"
        ),
        "language": Description(
            en="Language code (e.g., en, zh) or None for auto-detect",
            zh="语言代码（如 en, zh）或留空以自动检测",
        ),
        "device": Description(
            en="Device to use for inference (cpu, cuda, or auto)",
            zh="推理设备（cpu、cuda 或 auto）",
        ),
    }


class WhisperCPPConfig(I18nMixin):
    """Configuration for WhisperCPP ASR."""

    model_name: str = Field(..., alias="model_name")
    model_dir: str = Field(..., alias="model_dir")
    print_realtime: bool = Field(False, alias="print_realtime")
    print_progress: bool = Field(False, alias="print_progress")
    language: Literal["auto", "en", "zh"] = Field("auto", alias="language")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "model_name": Description(
            en="Name of the Whisper model", zh="Whisper 模型名称"
        ),
        "model_dir": Description(
            en="Directory containing Whisper models", zh="Whisper 模型目录"
        ),
        "print_realtime": Description(
            en="Print output in real-time", zh="实时打印输出"
        ),
        "print_progress": Description(
            en="Print progress information", zh="打印进度信息"
        ),
        "language": Description(
            en="Language code (en, zh, or auto)", zh="语言代码（en、zh 或 auto）"
        ),
    }






class ASRConfig(I18nMixin):
    """Configuration for Automatic Speech Recognition."""

    asr_model: Literal[
        "faster_whisper",
        "whisper_cpp",
    ] = Field(..., alias="asr_model")

    faster_whisper: Optional[FasterWhisperConfig] = Field(None, alias="faster_whisper")
    whisper_cpp: Optional[WhisperCPPConfig] = Field(None, alias="whisper_cpp")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "asr_model": Description(
            en="Speech-to-text model to use", zh="要使用的语音识别模型"
        ),
        "faster_whisper": Description(
            en="Configuration for Faster Whisper", zh="Faster Whisper 配置"
        ),
        "whisper_cpp": Description(
            en="Configuration for WhisperCPP", zh="WhisperCPP 配置"
        ),
    }

    @model_validator(mode="after")
    def check_asr_config(cls, values: "ASRConfig", info: ValidationInfo):
        asr_model = values.asr_model

        # Only validate the selected ASR model
        if asr_model == "faster_whisper" and values.faster_whisper is not None:
            values.faster_whisper.model_validate(values.faster_whisper.model_dump())
        elif asr_model == "whisper_cpp" and values.whisper_cpp is not None:
            values.whisper_cpp.model_validate(values.whisper_cpp.model_dump())

        return values