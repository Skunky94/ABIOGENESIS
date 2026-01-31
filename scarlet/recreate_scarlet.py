#!/usr/bin/env python3
"""
Recreate Scarlet agent with complete configuration.

WARNING: This will DELETE the existing Scarlet agent and all its memory.
Run this script to apply the new configuration.
"""

import requests

LETTA_URL = "http://localhost:8283"
AGENT_ID = "agent-ed8a8d29-75eb-4543-b4f7-59745589c07c"

def main():
    print("=== Scarlet Agent Recreation ===\n")
    
    # Step 1: Check current agent
    print("1. Checking current agent...")
    response = requests.get(f"{LETTA_URL}/v1/agents/{AGENT_ID}")
    if response.status_code == 200:
        agent = response.json()
        print(f"   Found: {agent['name']} (type: {agent.get('agent_type', 'unknown')})")
        print(f"   Sleep-time enabled: {agent.get('enable_sleeptime', False)}")
        print(f"   Context window: {agent.get('llm_config', {}).get('context_window', 'unknown')}")
    else:
        print("   Agent not found (may have been deleted already)")
        agent = None
    
    # Step 2: Confirm deletion
    print("\n2. WARNING: About to DELETE existing agent and ALL its memory!")
    confirm = input("   Continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("   Cancelled.")
        return
    
    # Step 3: Delete existing agent
    if agent:
        print("\n3. Deleting existing agent...")
        response = requests.delete(f"{LETTA_URL}/v1/agents/{AGENT_ID}")
        if response.status_code in [200, 204]:
            print("   ✓ Agent deleted successfully")
        else:
            print(f"   ✗ Failed to delete: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return
    
    # Step 4: Recreate with new config
    print("\n4. Agent deleted. You can now run scarlet_agent.py to create a new agent.")
    print("   The new agent will have:")
    print("   - Full Italian memory blocks (persona, human, goals, session_context, constraints)")
    print("   - Context window: 200,000 tokens")
    print("   - Embedding: BGE-m3")
    print("   - Sleep-time: enabled")
    print("   - Agent type: letta_v1_agent")
    print("\n   Run: python -c 'from scarlet_agent import ScarletAgent; ScarletAgent().create()'")

if __name__ == "__main__":
    main()
