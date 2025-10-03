from typing import (
    AsyncIterator,
    List,
    Dict,
    Any,
    Callable,
    Literal,
    Union,
    Optional,
)
from loguru import logger
from .agent_interface import AgentInterface
from ..output_types import SentenceOutput, DisplayText
from ..stateless_llm.stateless_llm_interface import StatelessLLMInterface
from ...chat_history_manager import get_history
from ..transformers import (
    sentence_divider,
    actions_extractor,
    tts_filter,
    display_processor,
)
from ...config_manager import TTSPreprocessorConfig
from ..input_types import BatchInput, TextSource, BaseInput
from ..output_types import BaseOutput
from prompts import prompt_loader


class BasicMemoryAgent(AgentInterface):
    """Simplified Agent with basic chat memory for Agent-Zero only."""

    _system: str = "You are a helpful assistant."

    def __init__(
        self,
        llm: StatelessLLMInterface,
        system: str,
        live2d_model,
        tts_preprocessor_config: TTSPreprocessorConfig = None,
        faster_first_response: bool = True,
        segment_method: str = "pysbd",
        interrupt_method: Literal["system", "user"] = "user",
        tts_enabled: bool = True,
    ):
        """Initialize agent with LLM and configuration."""
        super().__init__()
        self._memory = []
        self._live2d_model = live2d_model
        self._tts_preprocessor_config = tts_preprocessor_config
        self._faster_first_response = faster_first_response
        self._segment_method = segment_method
        self.interrupt_method = interrupt_method
        self._interrupt_handled = False
        self.prompt_mode_flag = False
        self.tts_enabled = tts_enabled

        self._set_llm(llm)
        self.set_system(system if system else self._system)

        logger.info("BasicMemoryAgent initialized for Agent-Zero only.")

    def _set_llm(self, llm: StatelessLLMInterface):
        """Set the LLM for chat completion."""
        self._llm = llm
        self.chat = self._chat_function_factory()

    def _chat_function_factory(self) -> Callable:
        """Create a chat function with transformers applied."""

        @tts_filter(self._tts_preprocessor_config)
        @display_processor()
        @actions_extractor(self._live2d_model)
        @sentence_divider(
            faster_first_response=self._faster_first_response,
            segment_method=self._segment_method,
            valid_tags=["think"],
        )
        async def chat_completion(
            messages: List[Dict[str, Any]]
        ) -> AsyncIterator[str]:
            """Chat completion with transformers applied."""
            async for token in self._llm.chat_completion(
                messages=messages,
                model="agent-zero",
                temperature=1.0,
                live2d_model=self._live2d_model,
            ):
                yield token

        return chat_completion

    def set_system(self, system: str):
        """Set system prompt."""
        self._system = system
        logger.debug(f"Memory Agent: Setting system prompt: '''{system}'''")

    def get_memory(self):
        """Get current memory/conversation history."""
        return self._memory

    def load_memory_from_list(self, history_list: List[Dict[str, Any]]):
        """Load memory from conversation history list."""
        self._memory = history_list
        logger.info(f"Loaded {len(history_list)} messages from history.")

    def _to_messages(self, input_data: BatchInput) -> List[Dict[str, str]]:
        """Convert input to message format."""
        messages = [{"role": "system", "content": self._system}]

        # Add memory/history
        messages.extend(self._memory)

        # Add current input
        for item in input_data.items:
            if item.source == TextSource.USER:
                messages.append({"role": "user", "content": item.text})
            elif item.source == TextSource.ASSISTANT:
                messages.append({"role": "assistant", "content": item.text})

        return messages

    async def chat_with_memory(
        self, input_data: BatchInput
    ) -> AsyncIterator[SentenceOutput]:
        """Process input and generate response with memory."""
        try:
            logger.info("Starting simple chat completion.")

            messages = self._to_messages(input_data)

            # Generate response
            async for output in self.chat(messages):
                yield output

            # Update memory with the conversation
            for item in input_data.items:
                if item.source == TextSource.USER:
                    self._memory.append({"role": "user", "content": item.text})

        except Exception as e:
            logger.error(f"Error in chat_with_memory: {e}")
            # Return error as sentence output
            error_output = SentenceOutput(
                display_text=DisplayText(text="Sorry, I encountered an error."),
                tts_text="Sorry, I encountered an error.",
                actions=None,
            )
            yield error_output

    def clear_memory(self):
        """Clear conversation memory."""
        self._memory = []
        logger.info("Memory cleared.")

    async def interrupt(self, input_data: BatchInput) -> AsyncIterator[SentenceOutput]:
        """Handle interruption (simplified for Agent-Zero)."""
        self._interrupt_handled = True
        logger.info("Interrupt handled.")

        # For Agent-Zero, we'll just process the new input
        async for output in self.chat_with_memory(input_data):
            yield output

    # Abstract methods from AgentInterface
    async def chat(self, input_data: BaseInput) -> AsyncIterator[BaseOutput]:
        """Chat with the agent (required by AgentInterface)."""
        if isinstance(input_data, BatchInput):
            async for output in self.chat_with_memory(input_data):
                yield output
        else:
            # Convert to BatchInput if needed
            batch_input = BatchInput(items=[input_data])
            async for output in self.chat_with_memory(batch_input):
                yield output

    def handle_interrupt(self, heard_response: str) -> None:
        """Handle interruption (required by AgentInterface)."""
        self._interrupt_handled = True
        logger.info(f"Interrupt handled. Heard response: {heard_response}")

    def set_memory_from_history(self, conf_uid: str, history_uid: str) -> None:
        """Load memory from history (required by AgentInterface)."""
        try:
            history_list = get_history(conf_uid, history_uid)
            self.load_memory_from_list(history_list)
        except Exception as e:
            logger.error(f"Failed to load history {history_uid}: {e}")
            self._memory = []