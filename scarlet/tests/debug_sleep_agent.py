"""
Debug: Check sleep agent messages and response format
"""

import httpx
import json

LETTA_URL = "http://localhost:8283"
SLEEP_AGENT_ID = "agent-3dd9a54f-dc55-4d7f-adc3-d5cbb1aca950"

def debug_sleep_agent():
    print("=" * 70)
    print("DEBUG: Sleep Agent Messages")
    print("=" * 70)
    
    # Get messages
    response = httpx.get(
        f"{LETTA_URL}/v1/agents/{SLEEP_AGENT_ID}/messages",
        params={"limit": 10},
        follow_redirects=True,
        timeout=30.0
    )
    response.raise_for_status()
    data = response.json()
    
    print(f"\nResponse type: {type(data)}")
    print(f"Response length: {len(data) if isinstance(data, list) else 'N/A'}")
    
    if isinstance(data, list):
        for i, msg in enumerate(data):
            print(f"\n--- Message {i+1} ---")
            print(f"Type: {type(msg)}")
            if isinstance(msg, dict):
                print(f"Keys: {msg.keys()}")
                if "content" in msg:
                    content = msg["content"]
                    print(f"Content type: {type(content)}")
                    print(f"Content preview: {str(content)[:300]}...")
                    
                    # Check if this is JSON
                    if isinstance(content, str) and content.strip().startswith("{"):
                        try:
                            parsed = json.loads(content)
                            print(f"\n  ✓ Valid JSON found!")
                            print(f"  Keys: {parsed.keys()}")
                        except Exception as e:
                            print(f"  ✗ Not valid JSON: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    debug_sleep_agent()
