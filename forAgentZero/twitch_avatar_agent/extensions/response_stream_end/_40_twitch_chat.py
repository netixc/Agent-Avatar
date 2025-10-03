"""
Twitch Chat Response Extension
Sends agent responses back to Twitch chat (ONCE when complete)
"""

import re
from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle


class TwitchChatExtension(Extension):
    """Sends complete responses to Twitch chat for Twitch messages"""

    # Class variable to accumulate response during streaming
    _accumulated_response = ""

    async def execute(self, loop_data=None, **kwargs):
        # Check if this is a response to a Twitch message
        if not self.agent.data.get("is_twitch_message"):
            return

        # Check if Twitch bot is available
        if "twitch_bot" not in self.agent.data:
            return

        # Get config
        config = self.agent.data.get("twitch_config", {})
        send_to_chat = config.get("send_to_chat", True)
        chat_max_length = config.get("chat_max_length", 500)

        if not send_to_chat:
            return

        # Get the accumulated response from class variable
        # (This was built up during response_stream hook by VTube extension)
        response_text = self.agent.data.get("_last_response_text", "").strip()

        if not response_text:
            # Fallback: try to get from history
            if self.agent.history.messages:
                last_msg = self.agent.history.messages[-1]
                if hasattr(last_msg, 'content'):
                    response_text = str(last_msg.content).strip()

        if not response_text:
            PrintStyle(font_color="yellow", padding=True).print(
                "⚠️ No response text found for Twitch chat"
            )
            return

        # Clean response (remove emotion tags like [joy], [neutral], etc.)
        clean_response = re.sub(
            r'\[(?:joy|neutral|sadness|anger|surprise|fear|disgust|smirk)\]',
            '',
            response_text
        ).strip()

        # Truncate if too long
        if len(clean_response) > chat_max_length:
            clean_response = clean_response[:chat_max_length - 3] + "..."

        # Send to Twitch chat
        bot = self.agent.data["twitch_bot"]
        if bot and bot.connected_channels:
            try:
                # Get the first connected channel
                channel = bot.connected_channels[0]
                await channel.send(clean_response)
                PrintStyle(font_color="green", padding=True).print(
                    f"💬 Sent to Twitch chat: {clean_response[:100]}..."
                )
            except Exception as e:
                PrintStyle(font_color="red", padding=True).print(
                    f"❌ Failed to send Twitch chat message: {e}"
                )
