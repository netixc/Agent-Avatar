# VTube Fast Agent

A high-speed AI stream companion optimized for fast responses without memory operations.

## Features

- **Maximum Speed**: No memory save/load operations - responds instantly
- **Stream Companion Personality**: Natural, entertaining conversation style
- **Emotion Tag Support**: Automatic emotion tags for Live2D expressions
- **Tool Access**: Full access to homeassistant, code execution, web search, etc.
- **No Twitch Integration**: Designed for private owner use only

## When to Use This Agent

- **For VTube streaming WITHOUT Twitch chat integration**
- When you want the fastest possible responses
- When you don't need the agent to remember past conversations
- For real-time interactions where speed is critical

## When NOT to Use This Agent

- ❌ If you need Twitch chat integration (use `twitch_avatar_agent` instead)
- ❌ If you want the agent to remember information between sessions
- ❌ If you need conversation history tracking

## Structure

```
vtube_fast_agent/
├── _context.md                                # Agent description
├── prompts/
│   ├── agent.system.main.role.md              # Stream companion personality
│   └── agent.system.tool.response.md          # Response tool with emotion tags
├── tools/
│   ├── response.py                            # Custom response with emotion validation
│   ├── memory_load.py                         # Disabled (empty stub)
│   ├── memory_save.py                         # Disabled (empty stub)
│   ├── memory_delete.py                       # Disabled (empty stub)
│   └── memory_forget.py                       # Disabled (empty stub)
└── extensions/
    ├── agent_init/
    │   └── _10_vtube_init.py                  # Initializes agent name
    └── response_stream/
        └── _30_vtube_simple.py                # Sends responses to Agent-Avatar with TTS
```

## Installation

Copy to your Agent-Zero installation:

```bash
cp -r vtube_fast_agent /path/to/agent-zero-data/agents/
```

**Location:** `/agent-zero-data/agents/vtube_fast_agent/`

## Configuration

### Agent-Avatar Configuration

Update your `conf.yaml` to use this agent:

```yaml
system_config:
  agent_zero_context_id: "vtube_fast_agent"
```

### In Agent-Zero Frontend

Navigate to agent selection and choose **`vtube_fast_agent`** as your active agent.

### Restart Agent-Avatar

```bash
docker compose restart
```

## How It Works

### Speed Optimization

The agent disables all memory operations by overriding memory tools with empty stubs:
- `memory_load.py` - Returns immediately without loading memories
- `memory_save.py` - Returns immediately without saving memories
- `memory_delete.py` - Returns immediately without deleting memories
- `memory_forget.py` - Returns immediately without forgetting memories

This eliminates database queries and vector operations that slow down responses.

### What You Keep

- ✅ All homeassistant tools (lights, TV, etc.)
- ✅ Code execution
- ✅ Web search
- ✅ Browser automation
- ✅ Document queries
- ✅ All other tools except memory

### What You Lose

- ❌ Memory persistence between conversations
- ❌ Twitch security (not needed for private use)
- ❌ Long-term information storage

## Personality

The agent acts as a **stream buddy** rather than a formal assistant:

- ✅ **Casual and fun**: "Hey! That's awesome!"
- ✅ **Expressive**: Uses emotion tags naturally
- ✅ **Fast**: No memory operations slow it down
- ❌ **Not formal**: No "How can I assist you today?"
- ❌ **No memory**: Lives in the moment

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

Example: `[joy] Hey there! [neutral] Let me turn on those lights for you.`

## Comparison with Twitch Avatar Agent

| Feature | VTube Fast Agent | Twitch Avatar Agent |
|---------|------------------|---------------------|
| Speed | ⚡ Maximum | 🐢 Slower (memory ops) |
| Memory | ❌ Disabled | ✅ Enabled |
| Twitch Integration | ❌ No | ✅ Yes |
| Tool Access | ✅ Full | ✅ Full (owner only) |
| Privacy Protection | Not needed | ✅ Yes |
| Best For | Private streaming | Public Twitch streams |

## Customization

Edit the prompts to adjust personality:
- **prompts/agent.system.main.role.md** - Main personality and behavior
- **prompts/agent.system.tool.response.md** - Response guidelines and speed tips

To re-enable a memory tool, delete the corresponding file from `tools/` directory and the agent will use the default implementation.
