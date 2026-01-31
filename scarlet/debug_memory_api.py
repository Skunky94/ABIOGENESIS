"""
Debug: Check Letta client memory API structure
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from scarlet.src.scarlet_agent import ScarletAgent


def main():
    print("=" * 70)
    print("DEBUG: Letta Client Memory API")
    print("=" * 70)
    
    scarlet = ScarletAgent()
    scarlet._ensure_client()
    
    print(f"\nClient type: {type(scarlet._client)}")
    print(f"Client attributes: {[a for a in dir(scarlet._client) if not a.startswith('_')]}")
    
    # Check if memory exists directly on client
    if hasattr(scarlet._client, 'memory'):
        print(f"\n✓ Client has 'memory' attribute")
        print(f"  Memory type: {type(scarlet._client.memory)}")
        print(f"  Memory attributes: {[a for a in dir(scarlet._client.memory) if not a.startswith('_')]}")
    else:
        print(f"\n✗ Client does NOT have 'memory' attribute")
    
    # Check agents.memory
    if hasattr(scarlet._client.agents, 'memory'):
        print(f"\n✓ Client.agents has 'memory' attribute")
    else:
        print(f"\n✗ Client.agents does NOT have 'memory' attribute")
    
    # Check blocks directly
    print(f"\nClient.agents.blocks attributes: {[a for a in dir(scarlet._client.agents.blocks) if not a.startswith('_')]}")
    
    # Get existing agent
    agents = list(scarlet._client.agents.list())
    agent = next((a for a in agents if a.name == "Scarlet"), None)
    
    if agent:
        print(f"\nFound agent: {agent.id}")
        
        # Try different APIs
        print("\nTrying memory APIs...")
        
        # Method 1: client.agents.blocks.list
        try:
            blocks = scarlet._client.agents.blocks.list(agent_id=agent.id)
            print(f"✓ client.agents.blocks.list(agent_id=...) works")
            print(f"  Result type: {type(blocks)}")
            print(f"  Blocks: {list(blocks)}")
        except Exception as e:
            print(f"✗ client.agents.blocks.list failed: {e}")
        
        # Method 2: client.memory (if exists)
        if hasattr(scarlet._client, 'memory'):
            try:
                blocks = scarlet._client.memory.blocks.list(agent_id=agent.id)
                print(f"✓ client.memory.blocks.list works")
            except Exception as e:
                print(f"✗ client.memory.blocks.list failed: {e}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
