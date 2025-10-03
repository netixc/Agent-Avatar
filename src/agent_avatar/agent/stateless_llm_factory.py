from typing import Type

from loguru import logger

from .stateless_llm.stateless_llm_interface import StatelessLLMInterface
from .stateless_llm.agent_zero_llm import AgentZeroLLM


class LLMFactory:
    @staticmethod
    def create_llm(llm_provider, **kwargs) -> Type[StatelessLLMInterface]:
        """Create an LLM based on the configuration.

        Only supports Agent-Zero LLM provider.

        Args:
            llm_provider: The type of LLM to create (must be "agent_zero_llm")
            **kwargs: Additional arguments
        """
        logger.info(f"Initializing LLM: {llm_provider}")

        if llm_provider == "agent_zero_llm":
            return AgentZeroLLM(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}. Only 'agent_zero_llm' is supported.")
