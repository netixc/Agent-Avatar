from agent import AgentContext, UserMessage
from python.helpers.api import ApiHandler, Request, Response
from python.helpers.print_style import PrintStyle
from python.helpers.defer import DeferredTask
import json
import asyncio


class VtubeMessageStream(ApiHandler):
    """
    Streaming API handler for receiving messages from Vtube-mcp.
    This enables real-time streaming responses as they are generated.
    """

    @classmethod
    def requires_loopback(cls) -> bool:
        return False  # Allow non-loopback since Vtube-mcp might be on different host

    @classmethod
    def requires_auth(cls) -> bool:
        return False  # No auth for now, can be enabled later

    @classmethod
    def requires_csrf(cls) -> bool:
        return False  # Disable CSRF for external API

    @classmethod
    def requires_api_key(cls) -> bool:
        return False  # Can be enabled for security later

    @classmethod
    def get_methods(cls) -> list[str]:
        return ["POST", "OPTIONS"]  # Support CORS preflight

    async def process(self, input: dict, request: Request) -> dict | Response:
        # Handle CORS preflight
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            return response

        # Extract message data
        text = input.get("text", "")
        source = input.get("source", "vtube")
        context_id = input.get("context", "")
        message_type = input.get("type", "text")  # text or audio_transcription
        user_id = input.get("user_id", "vtube_user")
        images = input.get("images", [])  # Extract images from VTube

        # Additional metadata for audio transcriptions
        confidence = input.get("confidence", 1.0)

        if not text:
            return {
                "success": False,
                "error": "No text provided"
            }

        # Add VTube emotion instruction (temporary fix until system prompt works)
        if not any(tag in text for tag in ["[joy]", "[sadness]", "[anger]", "[fear]", "[neutral]", "[surprise]", "[smirk]"]):
            emotion_prefix = "IMPORTANT: Use emotion tags like [joy], [sadness], [anger], [surprise], [fear], [neutral], [smirk] instead of emojis. "
            enhanced_text = emotion_prefix + text
        else:
            enhanced_text = text

        # Get or create context
        context = self.get_context(context_id)

        # Process images for Agent-Zero vision system
        image_paths = []
        if images:
            PrintStyle(font_color="cyan", padding=False).print(f"Processing {len(images)} images from VTube")
            import base64
            import tempfile
            import os

            for i, img in enumerate(images):
                try:
                    # Extract base64 data
                    base64_data = None
                    if isinstance(img, dict) and "data" in img:
                        # VTube sends images as {"source": "camera", "data": "data:image/jpeg;base64,xxx", "mime_type": "image/jpeg"}
                        data_url = img["data"]
                        if data_url.startswith("data:"):
                            # Extract base64 part from data URL
                            base64_data = data_url.split(",", 1)[1]
                        else:
                            base64_data = data_url
                    elif isinstance(img, str):
                        # In case images are sent as simple base64 strings
                        if img.startswith("data:"):
                            base64_data = img.split(",", 1)[1]
                        else:
                            base64_data = img

                    if base64_data:
                        # Decode and save to temporary file
                        image_data = base64.b64decode(base64_data)
                        temp_file = tempfile.NamedTemporaryFile(
                            suffix=f"_vtube_{i}.jpg",
                            delete=False,
                            dir="/tmp"
                        )
                        temp_file.write(image_data)
                        temp_file.close()
                        image_paths.append(temp_file.name)
                        PrintStyle(font_color="cyan", padding=False).print(f"Saved VTube image to: {temp_file.name}")

                except Exception as e:
                    PrintStyle(font_color="red", padding=False).print(f"Error processing VTube image {i}: {e}")

        # Log the incoming message
        PrintStyle(
            background_color="#FF6B6B", font_color="white", bold=True, padding=True
        ).print(f"Vtube streaming message received ({message_type}):")
        PrintStyle(font_color="white", padding=False).print(f"> {text}")
        if message_type == "audio_transcription":
            PrintStyle(font_color="white", padding=False).print(f"Confidence: {confidence:.2%}")
        if image_paths:
            PrintStyle(font_color="cyan", padding=False).print(f"Images: {len(image_paths)} saved to disk")

        # Log in agent context
        context.log.log(
            type="user",
            heading=f"Vtube {message_type}",
            content=text,
            kvps={
                "source": source,
                "type": message_type,
                "confidence": confidence if message_type == "audio_transcription" else None,
                "user_id": user_id,
                "images_count": len(image_paths)
            }
        )

        # If there are images, automatically trigger the vision_load tool first
        if image_paths:
            try:
                from python.tools.vision_load import VisionLoad

                PrintStyle(font_color="cyan", padding=False).print(f"Auto-triggering vision_load for {len(image_paths)} images")

                # Create and execute vision_load tool BEFORE sending the message
                vision_tool = VisionLoad(
                    agent=context.agent0,
                    name="vision_load",
                    method=None,
                    args={"paths": image_paths},
                    message="Auto-loading VTube images",
                    loop_data=None
                )
                await vision_tool.before_execution()
                response = await vision_tool.execute(paths=image_paths)
                await vision_tool.after_execution(response)

                # Now send enhanced message with image paths so agent knows where they are
                # Include the actual file paths in the message so the agent can reference them
                image_paths_str = ", ".join(image_paths)
                enhanced_text_with_images = (
                    enhanced_text +
                    f"\n\n(IMPORTANT: {len(image_paths)} image(s) have ALREADY been loaded by the vision_load tool. "
                    f"DO NOT call vision_load again - the images are already in your context and you can see them now. "
                    f"Just analyze what you see and respond directly. "
                    f"You CAN describe what people are doing, wearing, their environment, expressions, and general appearance. "
                    f"Just don't attempt to identify WHO they are by name.)"
                )
                task = context.communicate(UserMessage(enhanced_text_with_images, []))

            except Exception as e:
                PrintStyle(font_color="red", padding=False).print(f"Error auto-loading images: {e}")
                # Fall back to original message if vision loading fails
                task = context.communicate(UserMessage(enhanced_text, []))
        else:
            # Send enhanced message to agent (no images)
            task = context.communicate(UserMessage(enhanced_text, []))

        # Wait for complete result and return it
        # Note: Real-time streaming to VTube frontend happens via intercept extension
        # This endpoint provides the complete response for VTube's conversation flow
        try:
            # Wait for Agent-Zero to finish processing
            result = await task.result()

            # Return complete response as simple JSON (not SSE streaming)
            response_data = {
                "success": True,
                "message": result,
                "context_id": context.id
            }

            response = Response(
                response=json.dumps(response_data),
                status=200,
                mimetype="application/json"
            )
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response

        except Exception as e:
            PrintStyle.error(f"Error processing Vtube streaming message: {str(e)}")
            error_response = {
                "success": False,
                "error": str(e),
                "context": context.id
            }
            response = Response(
                response=json.dumps(error_response),
                status=500,
                mimetype="application/json"
            )
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response

    def _split_into_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences for streaming.
        """
        import re

        # Simple sentence splitting on punctuation
        sentences = re.split(r'([.!?]+)', text)
        result = []

        for i in range(0, len(sentences), 2):
            sentence = sentences[i].strip()
            if i + 1 < len(sentences):
                punctuation = sentences[i + 1]
                sentence += punctuation

            if sentence:
                result.append(sentence)

        # If no proper sentences found, split by length
        if not result or len(result) == 1:
            words = text.split()
            chunk_size = max(10, len(words) // 5)  # Split into ~5 chunks
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                if chunk:
                    result.append(chunk)

        return result if result else [text]