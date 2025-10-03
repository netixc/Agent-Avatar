from typing import Union, List, Dict, Any, Optional
import asyncio
import json
import re
from loguru import logger
import numpy as np

from .conversation_utils import (
    create_batch_input,
    process_agent_output,
    send_conversation_start_signals,
    process_user_input,
    finalize_conversation_turn,
    cleanup_conversation,
    EMOJI_LIST,
)
from .types import WebSocketSend
from .tts_manager import TTSTaskManager
from ..chat_history_manager import store_message
from ..service_context import ServiceContext
from ..agent_zero_client import get_agent_zero_client




def convert_agent_zero_to_vtube_format(text: str) -> str:
    """
    Convert Agent-Zero response format to Vtube expected format.
    This converts emojis to [emotion] tags that match the shizuku-local model.

    Supported emotions: neutral, anger, disgust, fear, joy, smirk, sadness, surprise
    """
    import re

    # Comprehensive emoji to emotion tag mapping for shizuku-local model
    emoji_map = {
        # Joy/Happy emotions (maps to expression 3)
        '😊': '[joy]',
        '😄': '[joy]',
        '😂': '[joy]',
        '🎉': '[joy]',
        '😃': '[joy]',
        '😁': '[joy]',
        '😆': '[joy]',
        '🥰': '[joy]',
        '😍': '[joy]',  # Love -> Joy

        # Sadness emotions (maps to expression 1)
        '😢': '[sadness]',
        '😭': '[sadness]',
        '😞': '[sadness]',
        '☹️': '[sadness]',
        '😔': '[sadness]',
        '😿': '[sadness]',

        # Anger emotions (maps to expression 2)
        '😠': '[anger]',
        '😡': '[anger]',
        '🤬': '[anger]',
        '😤': '[anger]',
        '💢': '[anger]',

        # Surprise emotions (maps to expression 3)
        '😮': '[surprise]',
        '😲': '[surprise]',
        '🤯': '[surprise]',
        '😱': '[surprise]',  # Also fear, but using surprise
        '🤔': '[surprise]',  # Thinking -> Surprise

        # Fear emotions (maps to expression 1)
        '😨': '[fear]',
        '😰': '[fear]',
        '😬': '[fear]',

        # Disgust emotions (maps to expression 2)
        '🤢': '[disgust]',
        '🤮': '[disgust]',
        '😖': '[disgust]',
        '🤧': '[disgust]',

        # Smirk emotions (maps to expression 3)
        '😏': '[smirk]',
        '😼': '[smirk]',
        '😎': '[smirk]',  # Cool -> Smirk

        # Other emojis mapped to appropriate emotions
        '😴': '[neutral]',  # Sleepy -> Neutral
        '🙄': '[disgust]',  # Eye roll -> Disgust
        '😵': '[surprise]', # Dizzy -> Surprise
    }

    result = text

    # Replace emojis with emotion tags
    for emoji, tag in emoji_map.items():
        result = result.replace(emoji, f' {tag}')

    # Clean up extra spaces
    result = re.sub(r'\s+', ' ', result).strip()

    return result


def extract_emotions_from_text(text: str, live2d_model) -> List[int]:
    """
    Extract emotions from Agent-Zero response text and map to Live2D expressions.

    Args:
        text: The response text from Agent-Zero
        live2d_model: The Live2D model with emotion mappings

    Returns:
        List of expression indices for Live2D
    """
    if not text:
        return [0]  # Default to neutral

    text_lower = text.lower()
    expressions = []

    # Emotion keyword mappings for Agent-Zero responses
    emotion_keywords = {
        'joy': ['😊', '😄', '😂', '🎉', '😃', 'happy', 'joy', 'excited', 'cheerful', 'glad', 'smile', 'laugh', 'joke'],
        'sadness': ['😢', '😭', '😞', 'sad', 'sorry', 'disappointed', 'upset', 'depressed', 'grief'],
        'anger': ['😠', '😡', '🤬', 'angry', 'mad', 'furious', 'irritated', 'annoyed', 'rage'],
        'surprise': ['😮', '😲', '🤯', 'wow', 'amazing', 'incredible', 'surprised', 'shocked', 'unexpected'],
        'fear': ['😨', '😰', '😱', 'scared', 'afraid', 'terrified', 'nervous', 'worried', 'anxious'],
        'disgust': ['🤢', '🤮', '😖', 'disgusting', 'gross', 'awful', 'terrible', 'yuck'],
        'smirk': ['😏', '😼', 'smirk', 'clever', 'sly', 'mischievous']
    }

    # Check for emotion keywords and emojis
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                if emotion in live2d_model.emo_map:
                    expressions.append(live2d_model.emo_map[emotion])
                    break

    # Also check for existing emotion tags like [happy], [sad], etc.
    existing_expressions = live2d_model.extract_emotion(text)
    expressions.extend(existing_expressions)

    # Remove duplicates and return, default to neutral if no emotions found
    expressions = list(set(expressions)) if expressions else [live2d_model.emo_map.get('neutral', 0)]

    return expressions


async def process_single_conversation(
    context: ServiceContext,
    websocket_send: WebSocketSend,
    client_uid: str,
    user_input: Union[str, np.ndarray],
    images: Optional[List[Dict[str, Any]]] = None,
    session_emoji: str = np.random.choice(EMOJI_LIST),
) -> str:
    """Process a single-user conversation turn

    Args:
        context: Service context containing all configurations and engines
        websocket_send: WebSocket send function
        client_uid: Client unique identifier
        user_input: Text or audio input from user
        images: Optional list of image data
        session_emoji: Emoji identifier for the conversation

    Returns:
        str: Complete response text
    """
    # Create TTSTaskManager for this conversation
    tts_manager = TTSTaskManager()

    try:
        # Send initial signals
        await send_conversation_start_signals(websocket_send)
        logger.info(f"New Conversation Chain {session_emoji} started!")

        # Process user input
        input_text = await process_user_input(
            user_input, context.asr_engine, websocket_send
        )

# Agent-Zero is now integrated directly as an LLM provider
        # No need for separate API calls

        # Create batch input
        batch_input = create_batch_input(
            input_text=input_text,
            images=images,
            from_name=context.character_config.human_name,
        )

        # Store user message
        if context.history_uid:
            store_message(
                conf_uid=context.character_config.conf_uid,
                history_uid=context.history_uid,
                role="human",
                content=input_text,
                name=context.character_config.human_name,
            )
        logger.info(f"User input: {input_text}")
        if images:
            logger.info(f"With {len(images)} images")

        # Process agent response using normal Vtube pipeline
        # Agent-Zero is now integrated as an LLM provider
        full_response = await process_agent_response(
            context=context,
            batch_input=batch_input,
            websocket_send=websocket_send,
            tts_manager=tts_manager,
        )

        # Wait for any pending TTS tasks
        if tts_manager.task_list:
            await asyncio.gather(*tts_manager.task_list)
            await websocket_send(json.dumps({"type": "backend-synth-complete"}))

        # For Agent-Zero: Give time for intercept extension streaming chunks to arrive and process
        # The intercept extension sends chunks to /stream/{history_uid} in real-time
        # We need to wait a bit to ensure all chunks are received and TTS is generated
        logger.info("⏳ Waiting for Agent-Zero streaming chunks to complete...")
        await asyncio.sleep(2.0)  # Give time for streaming chunks to arrive and process

        await finalize_conversation_turn(
            tts_manager=tts_manager,
            websocket_send=websocket_send,
            client_uid=client_uid,
        )

        if context.history_uid and full_response:
            store_message(
                conf_uid=context.character_config.conf_uid,
                history_uid=context.history_uid,
                role="ai",
                content=full_response,
                name=context.character_config.character_name,
                avatar=context.character_config.avatar,
            )
            logger.info(f"AI response: {full_response}")

        return full_response

    except asyncio.CancelledError:
        logger.info(f"🤡👍 Conversation {session_emoji} cancelled because interrupted.")
        raise
    except Exception as e:
        logger.error(f"Error in conversation chain: {e}")
        await websocket_send(
            json.dumps({"type": "error", "message": f"Conversation error: {str(e)}"})
        )
        raise
    finally:
        cleanup_conversation(tts_manager, session_emoji)


async def process_agent_response(
    context: ServiceContext,
    batch_input: Any,
    websocket_send: WebSocketSend,
    tts_manager: TTSTaskManager,
) -> str:
    """Process agent response and generate output

    Args:
        context: Service context containing all configurations and engines
        batch_input: Input data for the agent
        websocket_send: WebSocket send function
        tts_manager: TTSTaskManager for the conversation

    Returns:
        str: The complete response text
    """
    full_response = ""
    try:
        agent_output = context.agent_engine.chat(batch_input)
        async for output in agent_output:
            # Process agent output
            if isinstance(output, dict):
                # Skip dict outputs for now
                continue
            
            # Process non-dict outputs (SentenceOutput, etc.)
            # Get tts_enabled from agent if it's a BasicMemoryAgent
            tts_enabled = True
            if hasattr(context.agent_engine, 'tts_enabled'):
                tts_enabled = context.agent_engine.tts_enabled
            
            response_part = await process_agent_output(
                output=output,
                character_config=context.character_config,
                live2d_model=context.live2d_model,
                tts_engine=context.tts_engine,
                websocket_send=websocket_send,
                tts_manager=tts_manager,
                translate_engine=context.translate_engine,
                tts_enabled=tts_enabled,
            )
            logger.debug(f"Got response_part: {response_part} (type: {type(response_part)})")
            full_response += response_part

    except Exception as e:
        import traceback
        logger.error(f"Error processing agent response: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

    return full_response
