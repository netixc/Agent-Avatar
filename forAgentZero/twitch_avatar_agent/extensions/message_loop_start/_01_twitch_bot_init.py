"""
Twitch IRC Bot Extension for twitch_avatar_agent
Automatically starts Twitch bot when agent is active (runs on first message loop)
"""

import os
import asyncio
import yaml
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass, field
from twitchio.ext import commands
from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle
from python.helpers import files


@dataclass
class UserMessage:
    message: str
    attachments: list[str] = field(default_factory=list)
    system_message: list[str] = field(default_factory=list)


class TwitchBot(commands.Bot):
    """Twitch bot that listens for @mentions"""

    def __init__(
        self,
        token: str,
        channel: str,
        bot_name: str,
        message_callback: Callable[[str, str], Awaitable[None]],
    ):
        super().__init__(
            token=token,
            prefix="!",
            initial_channels=[channel]
        )
        self.bot_name = bot_name.lower()
        self.message_callback = message_callback
        self.channel_name = channel

    async def event_ready(self):
        """Called when bot successfully connects to Twitch"""
        PrintStyle(font_color="green", padding=True).print(
            f"✅ Twitch bot connected to channel: {self.channel_name}"
        )

    async def event_message(self, message):
        """Handle incoming chat messages"""
        # Ignore bot's own messages
        if message.echo:
            return

        # Check if bot is mentioned
        content = message.content.lower()
        mentions = [
            f"@{self.bot_name}",
            f"@{self.bot_name} ",
            self.bot_name,
        ]

        is_mentioned = any(mention in content for mention in mentions)

        if is_mentioned:
            # Extract the actual message (remove the @mention)
            text = message.content
            for mention in [f"@{self.bot_name}", self.bot_name]:
                text = text.replace(mention, "").replace(mention.capitalize(), "")
            text = text.strip()

            PrintStyle(font_color="cyan", padding=True).print(
                f"💬 Twitch message from {message.author.name}: {text}"
            )

            # Route to callback
            try:
                await self.message_callback(message.author.name, text)
            except Exception as e:
                PrintStyle(font_color="red", padding=True).print(
                    f"❌ Error processing Twitch message: {e}"
                )


class TwitchBotExtension(Extension):
    """Extension that starts Twitch bot when agent is active"""

    _bot_started = False  # Class-level flag to prevent multiple instances

    async def execute(self, loop_data=None, **kwargs):
        # CRITICAL: Only allow ONE bot globally
        if TwitchBotExtension._bot_started:
            return

        # Also check agent-level
        if "twitch_bot" in self.agent.data:
            return

        # Load config from agent's twitch_config.yaml
        config_path = files.get_abs_path(f"agents/{self.agent.config.profile}/twitch_config.yaml")

        if not os.path.exists(config_path):
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠️ Twitch config not found at {config_path}"
            )
            PrintStyle(font_color="yellow", padding=True).print(
                "Create twitch_config.yaml in the agent folder with oauth_token, channel, and bot_name"
            )
            return

        # Read config file
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            PrintStyle(font_color="red", padding=True).print(
                f"❌ Failed to load Twitch config: {e}"
            )
            return

        # Get required fields
        oauth_token = config.get("oauth_token", "")
        channel = config.get("channel", "")
        bot_name = config.get("bot_name", "")

        # Check if Twitch is configured
        if not oauth_token or not channel or not bot_name or oauth_token == "oauth:your_token_here":
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠️ Twitch not configured - edit {config_path} with your OAuth token, channel, and bot name"
            )
            return

        PrintStyle(font_color="green", padding=True).print(
            f"🚀 Starting Twitch bot for {self.agent.agent_name} on channel: {channel}"
        )

        # Store config
        self.agent.data["twitch_config"] = {
            "channel": channel,
            "message_prefix": config.get("message_prefix", "[Twitch]"),
            "send_to_chat": config.get("send_to_chat", True),
            "chat_max_length": config.get("chat_max_length", 500),
        }

        # Create and start bot
        async def handle_message(username: str, message: str):
            """Handle incoming Twitch messages by sending to agent"""
            # Only process messages when twitch_avatar_agent profile is active
            if self.agent.config.profile != "twitch_avatar_agent":
                PrintStyle(font_color="yellow", padding=True).print(
                    f"⚠️ Twitch message ignored - agent profile is '{self.agent.config.profile}' (not 'twitch_avatar_agent')"
                )
                return

            message_prefix = self.agent.data.get("twitch_config", {}).get("message_prefix", "[Twitch]")
            formatted_message = f"{message_prefix} {username} asks: {message}"

            PrintStyle(font_color="cyan", padding=True).print(
                f"📥 Received Twitch message: {formatted_message}"
            )

            # Mark current message as from Twitch (for security extension)
            self.agent.data["current_twitch_user"] = username
            self.agent.data["is_twitch_message"] = True

            # Send message to agent
            try:
                # Log the message to UI
                self.agent.context.log.log(
                    type="user",
                    heading=f"💬 Twitch: {username}",
                    content=message,
                )

                # Create UserMessage and add to history
                user_msg = UserMessage(message=formatted_message)
                self.agent.hist_add_user_message(user_msg)

                # Run the agent's monologue (message processing loop)
                await self.agent.monologue()
            except Exception as e:
                PrintStyle(font_color="red", padding=True).print(
                    f"❌ Error processing Twitch message: {e}"
                )
            finally:
                # Clean up markers
                self.agent.data.pop("current_twitch_user", None)
                self.agent.data.pop("is_twitch_message", None)

        bot = TwitchBot(
            token=oauth_token,
            channel=channel,
            bot_name=bot_name,
            message_callback=handle_message,
        )

        # Store bot for later use (sending messages)
        self.agent.data["twitch_bot"] = bot

        # Mark as started globally
        TwitchBotExtension._bot_started = True

        # Start bot in background task
        bot_task = asyncio.create_task(bot.start())
        self.agent.data["twitch_bot_task"] = bot_task

        PrintStyle(font_color="green", padding=True).print(
            f"✅ Twitch bot started for {self.agent.agent_name}"
        )
