from python.helpers.tool import Tool, Response
import re

class ResponseTool(Tool):

    async def execute(self, text="", **kwargs):
        # Validate emotion tags exist
        valid_emotions = ['joy', 'neutral', 'sadness', 'anger', 'surprise', 'fear', 'disgust', 'smirk']
        emotion_pattern = r'\[(' + '|'.join(valid_emotions) + r')\]'

        emotions_found = re.findall(emotion_pattern, text)

        if not emotions_found:
            # No emotion tags - add neutral at start
            text = "[neutral] " + text

        return Response(message=text, break_loop=True)

    async def before_execution(self, **kwargs):
        # Don't log here, handled by VTube extension
        pass

    async def after_execution(self, response, **kwargs):
        # Mark response as finished in logs
        if self.loop_data and "log_item_response" in self.loop_data.params_temporary:
            log = self.loop_data.params_temporary["log_item_response"]
            log.update(finished=True)
