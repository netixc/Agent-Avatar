#!/usr/bin/env python3
"""
Test script to find Agent-Zero API endpoints
"""

import asyncio
import aiohttp
import json

async def test_agent_zero_endpoints():
    """Test different Agent-Zero endpoints"""

    agent_zero_url = "http://192.168.50.67:50080"

    # Common API endpoints to test
    endpoints = [
        "/api",
        "/docs",
        "/openapi.json",
        "/v1/chat/completions",
        "/chat",
        "/message",
        "/vtube_message",
        "/upload",
        "/image",
        "/vision",
        "/analyze",
        "/process"
    ]

    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                url = f"{agent_zero_url}{endpoint}"
                print(f"\n=== Testing {endpoint} ===")

                # Test GET first
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    print(f"GET {endpoint}: Status {response.status}")
                    if response.status == 200:
                        try:
                            content = await response.text()
                            if content.startswith("{"):
                                data = json.loads(content)
                                print(f"JSON response: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                            else:
                                print(f"Response type: {response.content_type}")
                        except:
                            print("Response is not JSON")
                    elif response.status == 405:
                        print("Method not allowed (GET)")

                        # Try POST if GET is not allowed
                        try:
                            async with session.post(url,
                                                  json={"test": "data"},
                                                  timeout=aiohttp.ClientTimeout(total=3)) as post_response:
                                print(f"POST {endpoint}: Status {post_response.status}")
                        except Exception as e:
                            print(f"POST failed: {e}")

            except asyncio.TimeoutError:
                print(f"Timeout for {endpoint}")
            except Exception as e:
                print(f"Error for {endpoint}: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_zero_endpoints())