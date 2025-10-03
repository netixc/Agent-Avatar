"""
Twitch Message Injection Extension
Injects queued Twitch messages into the agent's message loop
"""

from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle


class TwitchMessageInjectExtension(Extension):
    """Injects Twitch messages from queue into agent loop"""

    async def execute(self, loop_data=None, **kwargs):
        # Check if Twitch message queue exists
        if "twitch_message_queue" not in self.agent.data:
            return

        queue = self.agent.data["twitch_message_queue"]

        # Check if there are any messages waiting
        if queue.empty():
            return

        # Get the next Twitch message (non-blocking)
        try:
            twitch_msg = queue.get_nowait()
        except:
            return

        # Get config
        config = self.agent.data.get("twitch_config", {})
        message_prefix = config.get("message_prefix", "[Twitch]")

        # Format message with prefix
        username = twitch_msg["username"]
        message = twitch_msg["message"]
        formatted_message = f"{message_prefix} {username} asks: {message}"

        PrintStyle(font_color="cyan", padding=True).print(
            f"📥 Injecting Twitch message: {formatted_message}"
        )

        # Inject into loop data as user message
        if loop_data:
            # Mark this as a Twitch message for later extensions
            loop_data.extras_temporary["is_twitch_message"] = True
            loop_data.extras_temporary["twitch_username"] = username

            # Add the message to history
            self.agent.hist_add_user(formatted_message)
