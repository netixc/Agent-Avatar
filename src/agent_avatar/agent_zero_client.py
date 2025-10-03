"""
Client for communicating with Agent-Zero API.
Handles sending messages and receiving responses from Agent-Zero.
"""

import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any
from loguru import logger


class AgentZeroClient:
    """Client for bidirectional communication with Agent-Zero"""

    def __init__(
        self,
        base_url: str,
        context_id: Optional[str] = None,
        enabled: bool = False
    ):
        """
        Initialize the Agent-Zero client.

        Args:
            base_url: Base URL for Agent-Zero API (default: http://localhost:50001)
            context_id: Optional context ID for maintaining conversation state
            enabled: Whether the client is enabled
        """
        self.base_url = base_url.rstrip("/")
        self.context_id = context_id or "avatar_context"
        self.enabled = enabled
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        if self.enabled:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def send_message_streaming(
        self,
        text: str,
        message_type: str = "text",
        user_id: str = "avatar_user",
        confidence: Optional[float] = None,
        images: Optional[list] = None
    ):
        """
        Send a message to Agent-Zero and wait for complete response.
        Real-time streaming happens via Agent-Zero's intercept extension.
        """
        if not self.enabled:
            logger.debug("Agent-Zero client is disabled")
            yield "Agent-Zero is disabled."
            return

        if not text or not text.strip():
            logger.warning("Empty message text")
            yield "Empty message received."
            return

        # Prepare the payload
        payload = {
            "text": text,
            "source": "avatar",
            "context": self.context_id,
            "type": message_type,
            "user_id": user_id
        }

        if confidence is not None and message_type == "audio_transcription":
            payload["confidence"] = confidence

        if images:
            payload["images"] = images
            logger.info(f"Including {len(images)} images in Agent-Zero message")

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            url = f"{self.base_url}/avatar_message_stream"
            logger.info(f"Sending message to Agent-Zero: {text[:50]}...")

            # Send request and wait for complete response
            # Real-time chunks are sent via intercept extension to /stream/{history_uid}
            async with self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "message" in data:
                        # Yield the complete response
                        yield data["message"]
                    else:
                        yield "Sorry, I encountered an error processing your request."
                else:
                    error_text = await response.text()
                    logger.error(f"Agent-Zero API error ({response.status}): {error_text}")
                    yield "Sorry, I encountered an error processing your request."

        except asyncio.TimeoutError:
            logger.error("Timeout while waiting for Agent-Zero")
            yield "Sorry, the response took too long to generate."
        except aiohttp.ClientError as e:
            logger.error(f"Network error communicating with Agent-Zero: {e}")
            yield "Sorry, I encountered a network error."
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            yield "Sorry, I encountered an unexpected error."


    def set_enabled(self, enabled: bool):
        """Enable or disable the Agent-Zero client"""
        self.enabled = enabled
        if enabled:
            logger.info("Agent-Zero client enabled")
        else:
            logger.info("Agent-Zero client disabled")

    def set_context_id(self, context_id: str):
        """Update the context ID for the conversation"""
        self.context_id = context_id
        logger.info(f"Updated Agent-Zero context ID to: {context_id}")

    def set_context_from_history(self, history_uid: str):
        """
        Set Agent-Zero context ID based on Avatar history UID.
        This ensures each Avatar chat creates a separate Agent-Zero context.

        Args:
            history_uid: Avatar history UID (e.g., "2025-01-15_14-30-45_abc123")
        """
        if history_uid:
            new_context_id = f"avatar_{history_uid}"
            self.set_context_id(new_context_id)
            logger.info(f"Synced Agent-Zero context with Avatar history: {history_uid}")
        else:
            # Fall back to default if no history_uid provided
            self.set_context_id("avatar_context")
            logger.warning("No history_uid provided, using default context")


# Global instance for easy access
_agent_zero_client: Optional[AgentZeroClient] = None


def get_agent_zero_client() -> AgentZeroClient:
    """Get the global Agent-Zero client instance"""
    global _agent_zero_client
    if _agent_zero_client is None:
        _agent_zero_client = AgentZeroClient()
    return _agent_zero_client


def init_agent_zero_client(
    base_url: str,
    context_id: Optional[str] = None,
    enabled: bool = False
) -> AgentZeroClient:
    """
    Initialize the global Agent-Zero client.

    Args:
        base_url: Base URL for Agent-Zero API
        context_id: Optional context ID for maintaining conversation state
        enabled: Whether the client is enabled

    Returns:
        The initialized client
    """
    global _agent_zero_client
    _agent_zero_client = AgentZeroClient(base_url, context_id, enabled)
    logger.info(f"Agent-Zero client initialized (enabled={enabled})")
    return _agent_zero_client