# config_manager/system.py
from pydantic import Field, model_validator
from typing import Dict, ClassVar, Optional
from .i18n import I18nMixin, Description


class SystemConfig(I18nMixin):
    """System configuration settings."""

    conf_version: str = Field(..., alias="conf_version")
    host: str = Field(..., alias="host")
    port: int = Field(..., alias="port")
    config_alts_dir: str = Field(..., alias="config_alts_dir")
    # tool_prompts removed - Agent-Zero handles emotions directly
    tool_prompts: Optional[Dict[str, str]] = Field(default_factory=dict, alias="tool_prompts")
    group_conversation_prompt: Optional[str] = Field(default=None, alias="group_conversation_prompt")

    # Agent-Zero integration settings
    agent_zero_enabled: bool = Field(False, alias="agent_zero_enabled")
    agent_zero_url: str = Field(..., alias="agent_zero_url")
    agent_zero_context_id: str = Field("vtube_context", alias="agent_zero_context_id")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "conf_version": Description(en="Configuration version", zh="配置文件版本"),
        "host": Description(en="Server host address", zh="服务器主机地址"),
        "port": Description(en="Server port number", zh="服务器端口号"),
        "config_alts_dir": Description(
            en="Directory for alternative configurations", zh="备用配置目录"
        ),
        "tool_prompts": Description(
            en="Tool prompts to be inserted into persona prompt",
            zh="要插入到角色提示词中的工具提示词",
        ),
        "agent_zero_enabled": Description(
            en="Enable Agent-Zero integration", zh="启用Agent-Zero集成"
        ),
        "agent_zero_url": Description(
            en="Agent-Zero API URL", zh="Agent-Zero API地址"
        ),
        "agent_zero_context_id": Description(
            en="Agent-Zero context ID for conversations", zh="Agent-Zero对话上下文ID"
        ),
    }

    @model_validator(mode="after")
    def check_port(cls, values):
        port = values.port
        if port < 0 or port > 65535:
            raise ValueError("Port must be between 0 and 65535")
        return values
