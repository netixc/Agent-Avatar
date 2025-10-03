# Agent-Avatar - Agent-Zero Powered Virtual Avatar

> **Desktop App with Pet Mode**: If you want a desktop application with pet mode functionality, check out [Agent-Avatar-App](https://github.com/netixc/Agent-Avatar-App)

## Available Live2D Models

**34 Total Models** featuring 15 unique characters:

- **Asuna** - 16 outfits (10 expressions, 16+ motions each)
- **Liko** - 10 outfits (10 expressions, 19 motions each)
- **Haru** - 1 outfit (5 expressions, 7 motions)
- **Shizuku** - 1 model (4 expressions, 18 motions with gesture support)
- **Epsilon** - 1 model (8 expressions, 15 motions)
- **Kato Megumi** - 1 model (6 expressions)
- **Tsukimi** - 1 model (10 expressions)
- **Mao Pro** - 1 model (8 expressions, SDK 3)
- **Natori** - 1 model (11 expressions, SDK 3)
- **RAYNOS-chan** - 1 model (8 expressions, SDK 3, VTube Studio optimized)
- **Erika, Mirai, Murakumo, Wanko, Yukari** - 1 model each

📖 **[View detailed model documentation](LIVE2D_MODELS.md)** - Complete list of expressions, motions, and interactive features for each character.

## Setup Kokoro-TTS

```bash
docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest 
```

## Setup Agent-Zero

```bash
docker pull agent0ai/agent-zero
mkdir agent-zero-data
docker run -p $50080:80 -v /path/to/your/agent-zero-data:/a0 agent0ai/agent-zero
```

## Requirements

- Docker and Docker Compose
- Agent-Zero AI framework (running on port 50080)
- TTS Server (Kokoro TTS recommended on port 8880)

## Quick Start

### Installation (Docker Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/netixc/Agent-Avatar.git
cd Agent-Avatar

# 2. Configure settings
cp config/templates/conf.default.yaml conf.yaml
nano conf.yaml  # Edit AGENT_ZERO_URL, TTS settings, etc.

# 3. Install Agent-Zero integration (REQUIRED)
# Read forAgentZero/README.md for instructions

# 4. Build and run with Docker Compose
docker compose up --build -d

# 5. Access VTube
open http://localhost:12393
```

## License

MIT License - See LICENSE file for details.
