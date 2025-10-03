# Agent-Zero Integration Files

This directory contains the required files to connect Agent-Avatar (Live2D VTube) with Agent-Zero.

## Requirements

- Agent-Zero
- Agent-Avatar running with Agent-Zero integration enabled (`agent_zero_enabled: true`)
- TTS server (e.g., Kokoro TTS)
- Network connectivity between Agent-Avatar and Agent-Zero

## Installation

Copy the files to your Agent-Zero installation:

### 1. Choose Your Agent

We provide two agents optimized for different use cases:

#### Option A: Twitch Avatar Agent (For Public Streaming with Twitch)
```bash
cp -r twitch_avatar_agent /path/to/agent-zero-data/agents/
```

**Location:** `/agent-zero-data/agents/twitch_avatar_agent/`

**Features:**
- Stream co-host personality (not a formal assistant)
- Automatic emotion tag validation
- Privacy protection for Twitch interactions
- Natural, engaging conversation style
- Full memory support for context retention

**Use when:** Streaming on Twitch with chat integration

**Then in Agent-Zero frontend:** Select agent `twitch_avatar_agent`

#### Option B: Avatar Fast Agent (For Private Use - Maximum Speed)
```bash
cp -r avatar_fast_agent /path/to/agent-zero-data/agents/
```

**Location:** `/agent-zero-data/agents/avatar_fast_agent/`

**Features:**
- ⚡ Maximum speed - no memory operations
- Stream companion personality
- Emotion tag support
- Full tool access (homeassistant, code, web, etc.)
- No Twitch integration needed

**Use when:** Private streaming or Avatar usage without Twitch, when you want the fastest responses

**Then in Agent-Zero frontend:** Select agent `avatar_fast_agent`

**Speed Comparison:**
- Avatar Fast Agent: ⚡ Instant responses (no database queries)
- Twitch Avatar Agent: 🐢 Slightly slower (memory operations enabled)

### 2. API Endpoint (receives messages from Agent-Avatar)
```bash
cp avatar_message_stream.py /path/to/python/api/
```

**Location:** `/python/api/avatar_message_stream.py`

This file handles incoming messages from Agent-Avatar and forwards them to Agent-Zero for processing.

### 3. Response Extension (Already Included in Agents)

The Avatar response extension is **already included** in both agent folders:
- `twitch_avatar_agent/extensions/response_stream/_30_avatar_simple.py`
- `avatar_fast_agent/extensions/response_stream/_30_avatar_simple.py`

**No separate installation needed!** When you copy the agent folder, the extension comes with it.

This extension streams Agent-Zero responses back to Agent-Avatar with TTS audio generation.

**Note:** The extension is **agent-specific** and only runs when you select `twitch_avatar_agent` or `avatar_fast_agent`. This is by design - other agents won't send responses to Agent-Avatar.

Both agents also include the `_30_avatar_simple.py` extension that handles streaming responses to Agent-Avatar.

## Switching Between Agents

**Easy!** Just select the agent in Agent-Zero's web interface. **No restart needed!**

### For Twitch Streaming:

1. Edit `twitch_config.yaml` in the `twitch_avatar_agent` folder (see agent README)
2. Select `twitch_avatar_agent` in Agent-Zero UI
3. Twitch bot auto-starts ✅

### For Private Use (No Twitch):

1. Select `avatar_fast_agent` in Agent-Zero UI
2. Twitch stays disabled ✅

**That's it!** The agent you select automatically enables/disables Twitch integration.

## Configuration

### Agent-Avatar Configuration

**Important:** The `agent_zero_context_id` in Agent-Avatar's `conf.yaml` is just a conversation session ID - it's NOT related to which agent profile you use. Agent selection happens in Agent-Zero's web UI.

All TTS settings are configured in Agent-Avatar's `conf.yaml`:

```yaml
tts_config:
  tts_model: "openai_tts"
  openai_tts:
    model: 'kokoro'
    voice: 'af_v0irulan+af_bella'
    api_key: 'not-needed'
    base_url: 'http://YOUR_TTS_SERVER_IP:8880/v1'
    response_format: 'mp3'
```

### Agent-Zero Configuration
The extension automatically fetches TTS configuration from Agent-Avatar's `/api/config` endpoint.

Default: `http://192.168.50.xx:12393`

**To change the default URL:** Edit `_30_vtube_simple.py` line 33

### Twitch Avatar Agent Configuration

The `twitch_avatar_agent` is already included in this directory and provides the best experience for streaming and Twitch integration.

**Features:**
- Stream co-host personality (not a formal assistant)
- Automatic emotion tag validation
- Privacy protection for Twitch interactions
- Natural, engaging conversation style

**After installation:**
1. In Agent-Zero frontend, select agent: **`twitch_avatar_agent`**
2. The agent will automatically use emotion tags and handle Twitch interactions properly

See `twitch_avatar_agent/README.md` for full documentation and customization options.

**Available emotion tags:**
- `[neutral]` - Default, calm expression
- `[joy]` - Happy, cheerful
- `[sadness]` - Sad, disappointed
- `[anger]` - Angry, frustrated
- `[surprise]` - Surprised, shocked
- `[fear]` - Scared, worried
- `[disgust]` - Disgusted, uncomfortable
- `[smirk]` - Smug, thinking, playful

Agent-Zero will automatically include emotion tags in responses, which Agent-Avatar will use to trigger the corresponding Live2D facial expressions.

## How It Works

1. **Agent-Avatar → Agent-Zero**: User speaks/types → Agent-Avatar sends message to Agent-Zero via `avatar_message_stream.py` API endpoint
2. **Agent-Zero Processing**: Agent-Zero processes the message and generates a response with emotion tags
3. **Agent-Zero → Agent-Avatar**: `_30_avatar_simple.py` extension intercepts the response, generates TTS audio, and streams it back to Agent-Avatar
4. **Agent-Avatar Display**: Agent-Avatar plays the audio and displays the text with Live2D animations

## Twitch Integration

When using the Twitch Avatar Agent, messages from Twitch chat (prefixed with `[Twitch]`) are automatically treated as public interactions, keeping your private conversations separate from stream viewers.

## Important: Agent-Zero Updates

When you update Agent-Zero, you'll need to re-apply one critical code change to maintain Twitch security:

### Code Change Required in `/agent-zero-data/agent.py`

Find the tool blocking code (around lines 776-803) and ensure it uses `extras_temporary` instead of `hist_add_warning` for Twitch security blocks:

```python
# Allow extensions to preprocess tool arguments (include loop_data for security checks)
tool_blocked = False
try:
    await self.call_extensions("tool_execute_before", tool_args=tool_args or {}, tool_name=tool_name, loop_data=self.loop_data)
except Exception as e:
    # Extension blocked the tool (e.g., Twitch security)
    error_msg = str(e)
    tool_blocked = True

    # Special handling for Twitch security blocks
    if "[Twitch Security]" in error_msg:
        # Add feedback as TEMPORARY extra - won't persist across iterations/messages
        # This gives immediate feedback for current iteration only, then auto-clears
        feedback_msg = f"⚠️ BLOCKED: Tool '{tool_name}' cannot be used for Twitch viewer messages. Use 'response' tool to chat with the viewer instead."
        self.loop_data.extras_temporary["twitch_security_block"] = feedback_msg
        PrintStyle(font_color="red", padding=True).print(error_msg)
        self.context.log.log(type="warning", content=f"{self.agent_name}: {error_msg}")
        # Continue loop so agent can use response tool in next iteration
    else:
        # For other errors, add to history normally
        self.hist_add_warning(error_msg)
        PrintStyle(font_color="red", padding=True).print(error_msg)
        self.context.log.log(type="warning", content=f"{self.agent_name}: {error_msg}")
        return None  # Skip tool execution, continue conversation

# Only execute tool if not blocked
if not tool_blocked:
    response = await tool.execute(**tool_args)
```

**Key changes:**
1. **Line with `loop_data=self.loop_data`**: Passes loop_data to extensions so Twitch security can check message prefix
2. **Uses `extras_temporary`**: Prevents Twitch blocks from polluting conversation history
3. **Checks `[Twitch Security]`**: Special handling for Twitch blocks vs other errors

**Why this is needed:**
- Without `extras_temporary`, security blocks stay in conversation history
- This causes the agent to treat owner messages as Twitch messages
- The owner loses access to tools after Twitch interactions

### Your Custom Prompts Are Safe

The following files in `twitch_avatar_agent/` will NOT be affected by Agent-Zero updates:
- `prompts/agent.system.main.role.md` - Anti-pattern-matching instructions
- `prompts/agent.system.response_tool_tips.md` - Twitch security guidelines
- `prompts/agent.system.tool.response.md` - Response tool override
- `extensions/` - All custom extensions
- `tools/` - Custom tools

These override the base agent and persist through updates.




