from python.helpers.tool import Tool, Response

# Custom response tool for VTube streamer agent
# Ensures emotion tags are present and validates format for TTS

class ResponseTool(Tool):

    async def execute(self, **kwargs):
        # Get the response text
        text = self.args.get("text", self.args.get("message", ""))

        # Ensure emotion tags are present (at least one)
        emotion_tags = ["[joy]", "[sadness]", "[anger]", "[surprise]", "[fear]", "[disgust]", "[smirk]", "[neutral]"]
        has_emotion = any(tag in text for tag in emotion_tags)

        # If no emotion tags, add a neutral one at the start
        if not has_emotion and text:
            text = "[neutral] " + text
            print("[VTube] Added missing emotion tag to response")

        return Response(message=text, break_loop=True)

    async def before_execution(self, **kwargs):
        # Don't log here, handled by live_response extension
        pass

    async def after_execution(self, response, **kwargs):
        # Mark response as finished in logs
        if self.loop_data and "log_item_response" in self.loop_data.params_temporary:
            log = self.loop_data.params_temporary["log_item_response"]
            log.update(finished=True)
