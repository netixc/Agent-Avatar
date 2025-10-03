# VTube Tests

This directory contains test files for the VTube project.

## Test Files:

- **`test_agent_zero_endpoints.py`** - Tests for Agent-Zero API endpoint integration
- **`test_agent_zero_image.py`** - Tests for Agent-Zero image processing functionality
- **`expression-test-universal.js`** - Browser-based Live2D expression tester

## Running Tests:

### Python Tests

To run the Python tests, make sure you have the VTube environment set up:

```bash
cd /root/vtube
uv run python tests/test_agent_zero_endpoints.py
uv run python tests/test_agent_zero_image.py
```

### Expression Testing (Browser Console)

The `expression-test-universal.js` file provides an interactive UI for testing Live2D model expressions directly in your browser:

**How to use:**

1. Open Agent-Avatar in your browser (http://localhost:12393)
2. Open the browser console (F12 or Right-click → Inspect → Console)
3. Copy the entire contents of `expression-test-universal.js`
4. Paste into the console and press Enter
5. A test panel will appear in the top-right corner
6. Click buttons to test each expression index (0-15)
7. Note which expression corresponds to each index for emotion mapping

**What it does:**

- Automatically detects the current Live2D model
- Creates an interactive panel with buttons for each expression index
- Allows you to test all expressions without triggering Agent-Zero
- Helps you create accurate `emotionMap` configurations in `model_dict.json`
- Provides immediate visual feedback

**Use case:** When configuring emotion mappings for a new Live2D model, use this tool to quickly identify which expression index corresponds to each emotion (neutral, joy, sadness, anger, etc.).

## Test Requirements:

- VTube server should be running for endpoint tests
- Agent-Zero should be accessible for integration tests
- Proper configuration in `conf.yaml`
- For expression testing: Browser with developer console access