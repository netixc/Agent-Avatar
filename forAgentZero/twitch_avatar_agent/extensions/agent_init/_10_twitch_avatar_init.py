from python.helpers.extension import Extension

# Twitch Avatar Agent initialization extension
# Sets a fun agent name and initializes stream companion mode

class TwitchAvatarInitExtension(Extension):

    async def execute(self, **kwargs):
        # Set a fun agent name for the stream
        self.agent.agent_name = "AgentAvatar" + str(self.agent.number)

        print(f"[Twitch Avatar] Initialized stream companion: {self.agent.agent_name}")
