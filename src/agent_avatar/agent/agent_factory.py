from typing import Type, Literal
from loguru import logger

from .agents.agent_interface import AgentInterface
from .agents.basic_memory_agent import BasicMemoryAgent
from .stateless_llm_factory import LLMFactory as StatelessLLMFactory


class AgentFactory:
    @staticmethod
    def create_agent(
        conversation_agent_choice: str,
        agent_settings: dict,
        llm_configs: dict,
        system_prompt: str,
        live2d_model=None,
        tts_preprocessor_config=None,
        **kwargs,
    ) -> Type[AgentInterface]:
        """Create an agent based on the configuration.

        Only supports basic_memory_agent with agent_zero_llm.

        Args:
            conversation_agent_choice: The type of agent to create (must be "basic_memory_agent")
            agent_settings: Settings for agent configuration
            llm_configs: LLM configurations (only agent_zero_llm supported)
            system_prompt: The system prompt to use
            live2d_model: Live2D model instance for expression extraction
            tts_preprocessor_config: Configuration for TTS preprocessing
            **kwargs: Additional arguments
        """
        logger.info(f"Initializing agent: {conversation_agent_choice}")

        if conversation_agent_choice == "basic_memory_agent":
            # Get the LLM provider choice from agent settings
            basic_memory_settings: dict = agent_settings.get("basic_memory_agent", {})
            llm_provider: str = basic_memory_settings.get("llm_provider", "agent_zero_llm")

            # Only support Agent-Zero LLM
            if llm_provider != "agent_zero_llm":
                raise ValueError(f"Unsupported LLM provider: {llm_provider}. Only 'agent_zero_llm' is supported.")

            # Get interrupt method from config
            llm_config: dict = llm_configs.get(llm_provider, {})
            interrupt_method: Literal["system", "user"] = llm_config.get("interrupt_method", "user")

            # Create the Agent-Zero LLM
            llm = StatelessLLMFactory.create_llm(
                llm_provider="agent_zero_llm",
                system_prompt=system_prompt
            )

            # Create the simplified agent
            return BasicMemoryAgent(
                llm=llm,
                system=system_prompt,
                live2d_model=live2d_model,
                tts_preprocessor_config=tts_preprocessor_config,
                faster_first_response=basic_memory_settings.get("faster_first_response", True),
                segment_method=basic_memory_settings.get("segment_method", "pysbd"),
                interrupt_method=interrupt_method,
                tts_enabled=basic_memory_settings.get("tts_enabled", True),
            )

        else:
            raise ValueError(f"Unsupported agent type: {conversation_agent_choice}. Only 'basic_memory_agent' is supported.")
