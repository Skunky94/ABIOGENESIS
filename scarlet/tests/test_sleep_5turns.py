"""
Real Test: Sleep-Time Activation with 5 Turns

Test Scenarios:
1. Send: "Ragiona sugli ultimi test, e sul tuo stato"
2. Send: "rifletti" (4 times)

Expected: Sleep-time should trigger after 5th message

Uses ONLY official agents:
- Primary: agent-0ef885f2-a9d9-4e9e-907a-7c6432004710
- Sleep:   agent-bc713153-a448-47f4-a26c-12bce2d64612
"""

import sys
import os
from pathlib import Path
import json
import time
import httpx

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Configuration
LETTA_URL = "http://localhost:8283"

# Official Agent IDs
PRIMARY_AGENT_ID = "agent-ac26cf86-3890-40a9-a70f-967f05115da9"
SLEEP_AGENT_ID = "agent-3dd9a54f-dc55-4d7f-adc3-d5cbb1aca950"

def send_message(agent_id: str, content: str) -> dict:
    """Send a message to an agent."""
    response = httpx.post(
        f"{LETTA_URL}/v1/agents/{agent_id}/messages",
        json={"messages": [{"role": "user", "content": content}]},
        timeout=120.0,
        follow_redirects=True
    )
    response.raise_for_status()
    return response.json()

def get_messages(agent_id: str, limit: int = 100) -> list:
    """Get messages from an agent."""
    response = httpx.get(
        f"{LETTA_URL}/v1/agents/{agent_id}/messages",
        params={"limit": limit},
        timeout=30.0,
        follow_redirects=True
    )
    response.raise_for_status()
    data = response.json()
    # Response is a list directly
    if isinstance(data, list):
        return data
    return data.get("messages", [])

def test_sleep_time_real():
    """Test sleep-time activation with 5 turns."""
    print("=" * 70)
    print("REAL TEST: Sleep-Time Activation with 5 Turns")
    print("=" * 70)
    
    # Verify agents exist
    print("\n[1] Verifying agents exist...")
    
    try:
        response = httpx.get(f"{LETTA_URL}/v1/agents/", timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        agents = response.json()  # Response is a list directly
        
        if not isinstance(agents, list):
            print(f"ERROR: Expected list, got {type(agents)}")
            return False
        agent_ids = [a.get("id") for a in agents]
        
        if PRIMARY_AGENT_ID not in agent_ids:
            print(f"ERROR: Primary agent {PRIMARY_AGENT_ID} not found!")
            return False
        print(f"  ✓ Primary agent found: {PRIMARY_AGENT_ID}")
        
        if SLEEP_AGENT_ID not in agent_ids:
            print(f"ERROR: Sleep agent {SLEEP_AGENT_ID} not found!")
            return False
        print(f"  ✓ Sleep agent found: {SLEEP_AGENT_ID}")
        
    except Exception as e:
        print(f"ERROR verifying agents: {e}")
        return False
    
    # Test messages to send
    messages = [
        "Ragiona sugli ultimi test, e sul tuo stato",
        "rifletti",
        "rifletti", 
        "rifletti",
        "rifletti"
    ]
    
    print(f"\n[2] Sending {len(messages)} messages (sleep should trigger after 5th)...")
    
    for i, msg in enumerate(messages, 1):
        print(f"\n  [{i}.{len(messages)}] Sending: '{msg}'")
        
        try:
            result = send_message(PRIMARY_AGENT_ID, msg)
            
            # Get last message content
            last_msg = result.get("messages", [])[-1] if result.get("messages") else {}
            content = last_msg.get("content", str(last_msg))
            print(f"  Response: {content[:150]}...")
            
            # Check if this was the 5th message (should trigger sleep)
            if i == 5:
                print("\n  *** 5th message - Sleep-time should trigger ***")
                time.sleep(3)  # Wait for consolidation
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n[3] Checking agent state after test...")
    
    # Get primary agent messages count
    primary_messages = get_messages(PRIMARY_AGENT_ID, limit=100)
    primary_count = len(primary_messages)
    print(f"  Primary agent messages: {primary_count}")
    
    # Get sleep agent messages
    sleep_messages = get_messages(SLEEP_AGENT_ID, limit=10)
    sleep_count = len(sleep_messages)
    print(f"  Sleep agent messages: {sleep_count}")
    
    if sleep_count > 0:
        print("\n  ✓ Sleep agent was invoked!")
        # Get last sleep message
        last_sleep = sleep_messages[-1]
        content = last_sleep.get("content", str(last_sleep))
        print(f"  Last sleep response:")
        print(f"  {content[:400]}...")
        
        # Try to parse JSON response
        try:
            # Find JSON in content
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                json_str = content[start:end+1]
                insights = json.loads(json_str)
                print(f"\n  Insights parsed:")
                print(f"    - persona_updates: {len(insights.get('persona_updates', []))}")
                print(f"    - human_updates: {len(insights.get('human_updates', []))}")
                print(f"    - goals_insights: {len(insights.get('goals_insights', []))}")
                print(f"    - reflection: {insights.get('reflection', 'N/A')[:100]}...")
        except Exception as e:
            print(f"  Could not parse JSON: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_sleep_time_real()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
