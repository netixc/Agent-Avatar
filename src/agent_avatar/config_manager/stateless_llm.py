# config_manager/llm.py
from typing import ClassVar, Literal
from pydantic import BaseModel, Field
from .i18n import I18nMixin, Description


class StatelessLLMBaseConfig(I18nMixin):
    """Base configuration for StatelessLLM."""

    # interrupt_method. If the provider supports inserting system prompt anywhere in the chat memory, use "system". Otherwise, use "user".
    interrupt_method: Literal["system", "user"] = Field(
        "user", alias="interrupt_method"
    )
    DESCRIPTIONS: ClassVar[dict[str, Description]] = {
        "interrupt_method": Description(
            en="""The method to use for prompting the interruption signal.
            If the provider supports inserting system prompt anywhere in the chat memory, use "system". 
            Otherwise, use "user". You don't need to change this setting.""",
            zh="""用于表示中断信号的方法(提示词模式)。如果LLM支持在聊天记忆中的任何位置插入系统提示词，请使用“system”。
            否则，请使用“user”。您不需要更改此设置。""",
        ),
    }


class AgentZeroConfig(StatelessLLMBaseConfig):
    """Configuration for Agent-Zero LLM."""

    system_prompt: str = Field(..., alias="system_prompt")
    interrupt_method: Literal["system", "user"] = Field(
        "user", alias="interrupt_method"
    )

    _AGENT_ZERO_DESCRIPTIONS: ClassVar[dict[str, Description]] = {
        "system_prompt": Description(
            en="System prompt for Agent-Zero", zh="Agent-Zero 系统提示词"
        ),
    }

    DESCRIPTIONS: ClassVar[dict[str, Description]] = {
        **StatelessLLMBaseConfig.DESCRIPTIONS,
        **_AGENT_ZERO_DESCRIPTIONS,
    }


class StatelessLLMConfigs(I18nMixin, BaseModel):
    """Pool of LLM provider configurations.
    This class contains configurations for Agent-Zero LLM only."""

    agent_zero_llm: AgentZeroConfig | None = Field(None, alias="agent_zero_llm")

    DESCRIPTIONS: ClassVar[dict[str, Description]] = {
        "agent_zero_llm": Description(
            en="Configuration for Agent-Zero LLM",
            zh="Agent-Zero LLM 配置",
        ),
    }
