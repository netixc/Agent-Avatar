from python.helpers.extension import Extension

# Twitch Tool Blocker Extension
# ONLY blocks tools when message is from Twitch viewers
# Owner can still use all tools normally

print("[Twitch Security] Tool blocker extension loaded!")

class TwitchToolBlocker(Extension):

    async def execute(self, **kwargs):
        """Block dangerous tools ONLY for Twitch viewer messages"""

        # Get tool_name and loop_data from kwargs
        tool_name = kwargs.get('tool_name')
        loop_data = kwargs.get('loop_data')

        if not tool_name or not loop_data:
            return

        # Get the user message from loop_data.user_message (which is a Message object)
        user_message = ""

        if hasattr(loop_data, 'user_message') and loop_data.user_message:
            msg_obj = loop_data.user_message
            # Message object should have a 'content' attribute
            if hasattr(msg_obj, 'content'):
                user_message = str(msg_obj.content)
            else:
                user_message = str(msg_obj)

        # Debug: Print the actual message being checked
        print(f"[Twitch Security DEBUG] Checking message for tool '{tool_name}': {user_message[:150]}")

        # Check if THIS specific message is from Twitch
        is_twitch_message = '[Twitch]' in user_message and 'asks:' in user_message

        if is_twitch_message:
            # This is a PUBLIC Twitch viewer message - block ALL tools except 'response'
            safe_tools = ['response']

            if tool_name not in safe_tools:
                print(f"[Twitch Security] ❌ BLOCKED tool '{tool_name}' for Twitch viewer")
                print(f"[Twitch Security] Message: {user_message[:100]}...")

                # Raise exception to prevent tool execution
                raise Exception(f"[Twitch Security] Tool '{tool_name}' is not allowed for Twitch viewers. Only 'response' tool is permitted.")
            else:
                print(f"[Twitch Security] ✅ Allowing safe tool '{tool_name}' for Twitch viewer")
        else:
            # This is a NORMAL message from the owner - allow all tools
            print(f"[Twitch Security] ✅ Owner message - allowing tool '{tool_name}'")
