# Twitch Avatar Agent

A fun, engaging AI stream companion designed for Agent-Avatar Live2D streaming and Twitch integration.

## Features

- **Stream Co-Host Personality**: Natural, entertaining conversation style (not a formal assistant)
- **Emotion Tag Support**: Automatic emotion tags for Live2D expressions
- **Privacy Protection**: Keeps private conversations separate from public Twitch interactions
- **Custom Response Tool**: Validates and ensures proper emotion tag formatting
- **Stream-Friendly**: Designed for public streaming interactions

## Structure

```
twitch_avatar_agent/
├── twitch_config.yaml                         # Twitch OAuth token and settings
├── prompts/
│   ├── agent.system.main.role.md              # Stream companion personality + Twitch security
│   ├── agent.system.response_tool_tips.md     # Agent-Avatar/Twitch guidelines
│   └── agent.system.tool.response.md          # Response tool override (CRITICAL for Twitch)
├── tools/
│   └── response.py                            # Custom response with emotion validation
└── extensions/
    ├── agent_init/
    │   ├── _05_twitch_bot.py                  # Twitch IRC bot (auto-starts with agent)
    │   └── _10_twitch_avatar_init.py          # Sets fun agent name
    ├── message_loop_start/
    │   └── _05_twitch_message_inject.py       # Injects Twitch messages into agent loop
    ├── tool_execute_before/
    │   └── _20_twitch_tool_blocker.py         # Blocks dangerous tools for Twitch viewers
    └── response_stream/
        ├── _30_vtube_simple.py                # Sends responses to Agent-Avatar with TTS
        └── _40_twitch_chat.py                 # Sends responses to Twitch chat
```

## Usage

### 1. Configure Twitch Settings

Edit the `twitch_config.yaml` file in the agent folder:

```yaml
# File: /agent-zero-data/agents/twitch_avatar_agent/twitch_config.yaml

oauth_token: "oauth:your_token_here"
channel: "your_channel_name"
bot_name: "your_bot_name"

# Optional settings:
send_to_chat: true              # Send AI responses back to Twitch chat
message_prefix: "[Twitch]"      # Prefix for messages sent to Agent-Zero
chat_max_length: 500            # Max chat message length
```

**How to get OAuth token:**
1. Go to https://twitchapps.com/tmi/
2. Click "Connect" and authorize
3. Copy the oauth token (starts with `oauth:`)
4. Paste it into `twitch_config.yaml`

### 2. In Agent-Zero Frontend

Navigate to agent selection and choose **`twitch_avatar_agent`** as your active agent.

### 3. Twitch Auto-Starts

**No restart needed!** When you select `twitch_avatar_agent` in Agent-Zero, the Twitch bot automatically starts. When you switch to a different agent, it automatically stops.

## Personality

The agent acts as a **stream buddy** rather than a formal assistant:

- ✅ **Casual and fun**: "Hey! That's awesome!"
- ✅ **Expressive**: Uses emotion tags naturally
- ✅ **Engaging**: Makes jokes, has opinions
- ❌ **Not formal**: No "How can I assist you today?"
- ❌ **Not robotic**: Feels natural and human-like

## Privacy

When interacting with Twitch viewers (messages prefixed with `[Twitch]`):
- Treats each question as a standalone public interaction
- Does NOT reveal private conversation history
- Does NOT mention internal tools or operations
- Keeps responses appropriate for public audience

## Customization

Edit the prompts to adjust personality:
- **prompts/agent.system.main.role.md** - Main personality, behavior, and Twitch security rules
- **prompts/agent.system.response_tool_tips.md** - Response guidelines and Twitch interaction examples
- **prompts/agent.system.tool.response.md** - Response tool override (ensures Twitch security checks happen first)

**Note:** The `agent.system.tool.response.md` file is CRITICAL - it overrides the base agent's response tool prompt to put Twitch security checks at the TOP, preventing the agent from trying other tools first.

## Emotion Tags

Always use emotion tags in responses:
- `[joy]` - Happy, excited
- `[neutral]` - Calm, normal
- `[sadness]` - Sad, disappointed
- `[anger]` - Angry, frustrated
- `[surprise]` - Surprised, shocked
- `[fear]` - Scared, worried
- `[disgust]` - Disgusted, repulsed
- `[smirk]` - Playful, mischievous

Example: `[joy] Hey there! [neutral] Welcome to the stream!`
