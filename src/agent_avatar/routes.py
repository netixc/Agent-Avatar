import json
from uuid import uuid4
import numpy as np
import asyncio
from datetime import datetime
from fastapi import APIRouter, WebSocket, UploadFile, File, Response, Request
from starlette.websockets import WebSocketDisconnect
from loguru import logger
from .service_context import ServiceContext
from .websocket_handler import WebSocketHandler
from .conversations.tts_manager import TTSTaskManager
from .agent.transformers import actions_extractor
from .agent.output_types import DisplayText, Actions

# Simple response_id tracking for stop commands
stopped_response_ids = set()


def init_client_ws_route(default_context_cache: ServiceContext):
    """
    Create and return API routes for handling the `/client-ws` WebSocket connections.

    Args:
        default_context_cache: Default service context cache for new sessions.

    Returns:
        tuple: (APIRouter, WebSocketHandler) - Configured router and handler instance
    """

    router = APIRouter()
    ws_handler = WebSocketHandler(default_context_cache)

    # Create TTS manager for streaming chunks
    streaming_tts_manager = TTSTaskManager()

    async def process_chunk_with_tts(chunk: str, context: ServiceContext, websocket_clients: list):
        """Process streaming chunk through TTS pipeline"""
        try:
            if not context.tts_engine or not context.live2d_model or not chunk.strip():
                return

            logger.debug(f"🎬 Processing streaming chunk for TTS: {chunk[:50]}...")

            # Extract emotions directly from the Live2D model
            expressions = context.live2d_model.extract_emotion(chunk)
            actions = Actions(expressions=expressions) if expressions else None

            # Create display text object (ensure no duration parameter)
            # Use only the specific fields we need to avoid any duration issues
            display_text = DisplayText(
                text=chunk,
                name="VTube AI",
                avatar="shizuku.png"
            )

            logger.debug(f"🎬 TTS text: {chunk}, Actions: {actions}")
            logger.debug(f"🔍 DisplayText object: {display_text}, type: {type(display_text)}")

            # Trigger TTS immediately - add more specific error handling
            try:
                # Ensure all parameters are properly typed for debugging
                websocket_func = websocket_clients[0][1].send_text if websocket_clients else None
                logger.debug(f"🔍 Parameters: tts_text={type(chunk)}, display_text={type(display_text)}, actions={type(actions)}")
                logger.debug(f"🔍 live2d_model={type(context.live2d_model)}, tts_engine={type(context.tts_engine)}")
                logger.debug(f"🔍 websocket_send={type(websocket_func)}")

                await streaming_tts_manager.speak(
                    tts_text=chunk,
                    display_text=display_text,
                    actions=actions,
                    live2d_model=context.live2d_model,
                    tts_engine=context.tts_engine,
                    websocket_send=websocket_func
                )
            except Exception as speak_error:
                logger.error(f"🚨 Exact TTS speak error: {speak_error}")
                logger.error(f"🚨 Error type: {type(speak_error)}")
                import traceback
                logger.error(f"🚨 Full traceback: {traceback.format_exc()}")
                # Don't raise to continue processing other chunks
                return

            logger.debug(f"✅ Successfully processed streaming chunk for TTS")

        except Exception as e:
            logger.error(f"❌ Error processing streaming chunk for TTS: {e}")

    @router.websocket("/client-ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for client connections"""
        await websocket.accept()
        client_uid = str(uuid4())

        try:
            await ws_handler.handle_new_connection(websocket, client_uid)
            await ws_handler.handle_websocket_communication(websocket, client_uid)
        except WebSocketDisconnect:
            await ws_handler.handle_disconnect(client_uid)
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {e}")
            await ws_handler.handle_disconnect(client_uid)
            raise
    
    @router.post("/api/external_audio")
    async def receive_external_audio(request: Request):
        """
        Receive audio with lip-sync data from external sources (like chatbots).
        Also handles stop_audio commands to clear the audio queue.
        
        This endpoint allows external applications to send audio with lip-sync data
        that will be broadcast to all connected VTube clients, or stop all audio.
        """
        try:
            data = await request.json()
            
            # Handle stop_audio command
            if data.get("type") == "stop_audio":
                response_id = data.get("response_id", "all")
                logger.info(f"Received stop_audio command from {data.get('source', 'unknown')} for response_id: {response_id}")
                
                # Mark response as stopped (for potential future use)
                if response_id == "all":
                    stopped_response_ids.clear()
                    stopped_response_ids.add("all")
                else:
                    stopped_response_ids.add(int(response_id))
                
                return {
                    "status": "success", 
                    "message": f"Acknowledged stop for response_id {response_id}"
                }
            
            # Regular audio handling - validate required fields
            if not data.get("audio"):
                return {"status": "error", "message": "Missing audio data"}
            
            if not data.get("volumes"):
                return {"status": "error", "message": "Missing volume data for lip-sync"}
            
            # Extract text from display_text for emotion detection
            display_text = data.get("display_text", {"text": ""})
            text = display_text.get("text", "")
            
            # Extract emotions from text if no actions provided
            actions = data.get("actions")
            if not actions and text and hasattr(ws_handler, 'default_context_cache'):
                try:
                    # Get the Live2D model from the default context
                    live2d_model = ws_handler.default_context_cache.live2d_model
                    if live2d_model:
                        # Extract emotions from text
                        expressions = live2d_model.extract_emotion(text)
                        if expressions:
                            actions = {"expressions": expressions}
                            logger.debug(f"Extracted expressions {expressions} from text: {text[:50]}...")
                except Exception as e:
                    logger.debug(f"Could not extract emotions: {e}")

            # Strip emotion tags from display text if display_clean flag is set
            if display_text.get("display_clean", False):
                import re
                clean_text = re.sub(r'\[(?:joy|sadness|anger|fear|neutral|surprise|smirk|disgust)\]\s*', '', display_text.get("text", ""), flags=re.IGNORECASE)
                display_text = {
                    "text": clean_text,
                    "duration": display_text.get("duration")
                }

            # Create audio payload for frontend
            audio_payload = {
                "type": "audio",
                "audio": data["audio"],
                "volumes": data["volumes"],
                "slice_length": data.get("slice_length", 20),
                "display_text": display_text,
                "actions": actions,  # Now includes extracted expressions
                "forwarded": False,
                "response_id": data.get("response_id", 0)  # Pass through response_id
            }
            
            # Log the request
            source = data.get("source", "unknown")
            text = data.get("display_text", {}).get("text", "")
            response_id = data.get("response_id", 0)
            logger.info(f"Received external audio from {source} (response_id: {response_id}): '{text[:50]}...'")
            
            # Send to connected clients immediately (Agent Zero now handles interruption)
            connected_clients = list(ws_handler.client_connections.keys())
            if connected_clients:
                success_count = 0
                for client_uid in connected_clients:
                    try:
                        websocket = ws_handler.client_connections.get(client_uid)
                        if websocket:
                            await websocket.send_text(json.dumps(audio_payload))
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send audio to client {client_uid}: {e}")
                
                logger.debug(f"Sent audio from response_id: {response_id} to {success_count} clients")
            
            return {
                "status": "success", 
                "message": f"Audio sent to {len(connected_clients)} clients",
                "clients_reached": success_count if 'success_count' in locals() else 0
            }
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return {"status": "error", "message": "Invalid JSON"}
        except Exception as e:
            logger.error(f"Error processing external audio: {e}")
            return {"status": "error", "message": str(e)}

    @router.post("/stream/{history_uid}")
    async def receive_stream_chunk(history_uid: str, request: Request):
        """
        Receive streaming text chunks from Agent-Zero for real-time display.
        This enables live text generation without waiting for complete response.
        """
        logger.info(f"🚀 Received streaming chunk for history {history_uid}")
        try:
            data = await request.json()
            logger.debug(f"📋 Stream data: {data}")

            chunk_type = data.get("type", "")
            if chunk_type != "stream_chunk":
                logger.error(f"❌ Invalid chunk type: {chunk_type}")
                return {"status": "error", "message": "Invalid chunk type"}

            context_id = data.get("context_id", "")
            chunk = data.get("chunk", "")
            is_final = data.get("is_final", False)

            logger.info(f"📝 Processing chunk: '{chunk[:50]}...' (final: {is_final})")

            if not chunk:
                logger.debug("⚠️ Empty chunk received")
                return {"status": "success", "message": "Empty chunk received"}

            # Find active WebSocket connections for this history
            matching_clients = []
            logger.debug(f"🔍 Searching for WebSocket clients with history_uid: {history_uid}")
            logger.debug(f"🔍 Available client contexts: {list(ws_handler.client_contexts.keys())}")

            logger.debug(f"🔍 client_connections keys: {list(ws_handler.client_connections.keys())}")

            for client_uid, context in ws_handler.client_contexts.items():
                logger.debug(f"🔍 Checking client {client_uid}, context: {context}")
                if hasattr(context, 'history_uid'):
                    logger.debug(f"🔍 Client {client_uid} has history_uid: {context.history_uid}")
                    # Match both with and without "vtube_" prefix
                    # Agent-Zero sends "vtube_XXX" but VTube stores "XXX"
                    client_history = context.history_uid
                    history_matches = (client_history == history_uid or
                                     f"vtube_{client_history}" == history_uid or
                                     client_history == history_uid.replace("vtube_", ""))

                    if history_matches:
                        websocket = ws_handler.client_connections.get(client_uid)
                        logger.debug(f"🔍 WebSocket for {client_uid}: {websocket is not None}")
                        if websocket:
                            matching_clients.append((client_uid, websocket))
                            logger.info(f"✅ Found matching client: {client_uid}")
                        else:
                            logger.error(f"❌ Client {client_uid} has context but NO websocket in client_connections!")

            logger.info(f"🎯 Found {len(matching_clients)} matching WebSocket clients")

            # Don't send text_stream to clients - audio messages already contain display_text
            # This prevents "Unknown message type: text_stream" warnings in frontend
            logger.debug(f"📝 Processing chunk (not sending text_stream): '{chunk[:30]}...'")

            # Get TTS context for processing
            tts_context = None
            if matching_clients:
                first_client_uid = matching_clients[0][0]
                tts_context = ws_handler.client_contexts.get(first_client_uid)

            if tts_context and tts_context.tts_engine and tts_context.live2d_model:
                try:
                    await process_chunk_with_tts(chunk, tts_context, matching_clients)
                except Exception as tts_error:
                    logger.error(f"❌ TTS processing failed: {tts_error}")

            return {
                "status": "success",
                "message": f"Chunk processed for TTS",
                "chunk_length": len(chunk)
            }

        except json.JSONDecodeError:
            logger.error("Invalid JSON in stream request")
            return {"status": "error", "message": "Invalid JSON"}
        except Exception as e:
            logger.error(f"Error processing stream chunk: {e}")
            return {"status": "error", "message": str(e)}



    return router, ws_handler


def init_webtool_routes(default_context_cache: ServiceContext) -> APIRouter:
    """
    Create and return API routes for handling web tool interactions.

    Args:
        default_context_cache: Default service context cache for new sessions.

    Returns:
        APIRouter: Configured router with WebSocket endpoint.
    """

    router = APIRouter()

    @router.get("/web-tool")
    async def web_tool_redirect():
        """Redirect /web-tool to /web_tool/index.html"""
        return Response(status_code=302, headers={"Location": "/web-tool/index.html"})

    @router.get("/web_tool")
    async def web_tool_redirect_alt():
        """Redirect /web_tool to /web_tool/index.html"""
        return Response(status_code=302, headers={"Location": "/web-tool/index.html"})

    @router.post("/asr")
    async def transcribe_audio(file: UploadFile = File(...)):
        """
        Endpoint for transcribing audio using the ASR engine
        """
        logger.info(f"Received audio file for transcription: {file.filename}")

        try:
            contents = await file.read()

            # Validate minimum file size
            if len(contents) < 44:  # Minimum WAV header size
                raise ValueError("Invalid WAV file: File too small")

            # Decode the WAV header and get actual audio data
            wav_header_size = 44  # Standard WAV header size
            audio_data = contents[wav_header_size:]

            # Validate audio data size
            if len(audio_data) % 2 != 0:
                raise ValueError("Invalid audio data: Buffer size must be even")

            # Convert to 16-bit PCM samples to float32
            try:
                audio_array = (
                    np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                    / 32768.0
                )
            except ValueError as e:
                raise ValueError(
                    f"Audio format error: {str(e)}. Please ensure the file is 16-bit PCM WAV format."
                )

            # Validate audio data
            if len(audio_array) == 0:
                raise ValueError("Empty audio data")

            text = await default_context_cache.asr_engine.async_transcribe_np(
                audio_array
            )
            logger.info(f"Transcription result: {text}")
            return {"text": text}

        except ValueError as e:
            logger.error(f"Audio format error: {e}")
            return Response(
                content=json.dumps({"error": str(e)}),
                status_code=400,
                media_type="application/json",
            )
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return Response(
                content=json.dumps(
                    {"error": "Internal server error during transcription"}
                ),
                status_code=500,
                media_type="application/json",
            )

    @router.websocket("/tts-ws")
    async def tts_endpoint(websocket: WebSocket):
        """WebSocket endpoint for TTS generation"""
        await websocket.accept()
        logger.info("TTS WebSocket connection established")

        try:
            while True:
                data = await websocket.receive_json()
                text = data.get("text")
                if not text:
                    continue

                logger.info(f"Received text for TTS: {text}")

                # Split text into sentences
                sentences = [s.strip() for s in text.split(".") if s.strip()]

                try:
                    # Generate and send audio for each sentence
                    for sentence in sentences:
                        sentence = sentence + "."  # Add back the period
                        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid4())[:8]}"
                        audio_path = (
                            await default_context_cache.tts_engine.async_generate_audio(
                                text=sentence, file_name_no_ext=file_name
                            )
                        )
                        logger.info(
                            f"Generated audio for sentence: {sentence} at: {audio_path}"
                        )

                        await websocket.send_json(
                            {
                                "status": "partial",
                                "audioPath": audio_path,
                                "text": sentence,
                            }
                        )

                    # Send completion signal
                    await websocket.send_json({"status": "complete"})

                except Exception as e:
                    logger.error(f"Error generating TTS: {e}")
                    await websocket.send_json({"status": "error", "message": str(e)})

        except WebSocketDisconnect:
            logger.info("TTS WebSocket client disconnected")
        except Exception as e:
            logger.error(f"Error in TTS WebSocket connection: {e}")
            await websocket.close()

    @router.get("/api/config")
    async def get_config():
        """
        Get VTube configuration for external integrations.
        Returns TTS settings and other relevant config.
        """
        try:
            context = default_context_cache
            config = {
                "tts": {
                    "base_url": context.character_config.tts_config.openai_tts.base_url if hasattr(context.character_config.tts_config, 'openai_tts') else None,
                    "model": context.character_config.tts_config.openai_tts.model if hasattr(context.character_config.tts_config, 'openai_tts') else None,
                    "voice": context.character_config.tts_config.openai_tts.voice if hasattr(context.character_config.tts_config, 'openai_tts') else None,
                },
                "vtube": {
                    "host": context.system_config.host,
                    "port": context.system_config.port,
                }
            }
            return config
        except Exception as e:
            logger.error(f"Error fetching config: {e}")
            return {"status": "error", "message": str(e)}

    return router
