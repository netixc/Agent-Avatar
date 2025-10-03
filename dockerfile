# Base image
FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu22.04 AS base

# Set noninteractive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies (this layer will be cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential libsndfile1 \
    git \
    curl \
    wget \
    ffmpeg \
    libportaudio2 \
    python3 \
    python3-pip \
    python3-dev \
    g++ \
    libopenblas-dev \
    && \
    rm -rf /var/lib/apt/lists/*

# Install uv and ensure it's accessible (this layer will be cached)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv
ENV PATH="/root/.local/bin:$PATH"

# Set working directory early for dependency installation
WORKDIR /app

# Copy only dependency files first (this allows Docker to cache the dependency installation)
COPY pyproject.toml uv.lock ./

# Install dependencies (this layer will be cached unless dependencies change)
RUN uv sync --no-dev

# TTS Engine: OpenAI-compatible TTS (external Kokoro server)
# Agent: Agent-Zero integration only

# Copy application code to the container (this layer will rebuild when code changes)
COPY . .

# Expose port 12393 (the new default port)
EXPOSE 12393

# Use uv to run the server in verbose mode for debugging
CMD ["uv", "run", "run_server.py", "--verbose"]
