#!/usr/bin/env python3
"""
Test script to directly send image data to Agent-Zero API
to understand the expected image format.
"""

import asyncio
import aiohttp
import json
import base64
from pathlib import Path

async def test_agent_zero_image():
    """Test sending an image to Agent-Zero API"""

    # Create a simple test image (1x1 pixel red PNG)
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

    # Test different image payload formats
    test_cases = [
        # Format 1: VTube current format
        {
            "name": "VTube format",
            "payload": {
                "text": "Can you see what's in this image?",
                "source": "vtube",
                "context": "vtube_context",
                "type": "text",
                "user_id": "vtube_user",
                "images": [{
                    "source": "camera",
                    "data": f"data:image/png;base64,{test_image_data}",
                    "mime_type": "image/png"
                }]
            }
        },
        # Format 2: Simple base64 format
        {
            "name": "Simple base64 format",
            "payload": {
                "text": "Can you see what's in this image?",
                "source": "vtube",
                "context": "vtube_context",
                "type": "text",
                "user_id": "vtube_user",
                "image": test_image_data
            }
        },
        # Format 3: Array of base64 strings
        {
            "name": "Array of base64 strings",
            "payload": {
                "text": "Can you see what's in this image?",
                "source": "vtube",
                "context": "vtube_context",
                "type": "text",
                "user_id": "vtube_user",
                "images": [test_image_data]
            }
        },
        # Format 4: Text only (control test)
        {
            "name": "Text only (control)",
            "payload": {
                "text": "Hello, can you respond to this message?",
                "source": "vtube",
                "context": "vtube_context",
                "type": "text",
                "user_id": "vtube_user"
            }
        }
    ]

    agent_zero_url = "http://192.168.50.67:50080"

    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            print(f"\n=== Testing {test_case['name']} ===")

            try:
                url = f"{agent_zero_url}/vtube_message"
                print(f"Sending to: {url}")
                print(f"Payload keys: {list(test_case['payload'].keys())}")

                async with session.post(
                    url,
                    json=test_case['payload'],
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    print(f"Status: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"Success: {data.get('success')}")
                        print(f"Response message: {data.get('message', 'No message')[:100]}...")
                    else:
                        error_text = await response.text()
                        print(f"Error: {error_text}")

            except Exception as e:
                print(f"Exception: {e}")

            # Wait between tests
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_agent_zero_image())