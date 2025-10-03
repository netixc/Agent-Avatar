"""
Twitch Chat Response Text Accumulator
Stores response text during streaming for later use by response_stream_end
"""

from python.helpers.extension import Extension


class TwitchChatAccumulator(Extension):
    """Accumulates response text during streaming for Twitch"""

    async def execute(self, loop_data=None, text="", parsed=None, **kwargs):
        # Only accumulate for Twitch messages
        if not self.agent.data.get("is_twitch_message"):
            return

        # Skip if not a response tool
        if (
            not parsed
            or not isinstance(parsed, dict)
            or parsed.get("tool_name") != "response"
            or "tool_args" not in parsed
            or "text" not in parsed["tool_args"]
        ):
            return

        # Store the latest response text for response_stream_end to use
        response_text = parsed["tool_args"]["text"].strip()
        if response_text:
            self.agent.data["_last_response_text"] = response_text
