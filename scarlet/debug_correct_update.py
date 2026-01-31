"""
Debug: Test correct update API
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
    print("DEBUG: Test correct blocks.update API")
    print("=" * 70)
    
    scarlet = ScarletAgent()
    scarlet._ensure_client()
    
    # Get an agent
    agents = list(scarlet._client.agents.list())
    agent = next((a for a in agents if a.name == "Scarlet"), None)
    
    if agent:
        print(f"\nAgent: {agent.id}")
        
        # Get current value
        current = scarlet._client.agents.blocks.retrieve(
            agent_id=agent.id,
            block_label="persona"
        )
        print(f"\nCurrent value: {current.value[:100]}...")
        print(f"Block ID: {current.id}")
        
        # Try update with block_label + agent_id + value
        print("\nTrying update with block_label...")
        try:
            new_value = f"[TEST UPDATE]\n\n{current.value}"
            result = scarlet._client.agents.blocks.update(
                block_label="persona",
                agent_id=agent.id,
                value=new_value
            )
            print(f"✓ Update worked!")
            print(f"  Result: {result}")
            
            # Verify
            verify = scarlet._client.agents.blocks.retrieve(
                agent_id=agent.id,
                block_label="persona"
            )
            print(f"  Verified value: {verify.value[:100]}...")
            
            # Restore original
            scarlet._client.agents.blocks.update(
                block_label="persona",
                agent_id=agent.id,
                value=current.value
            )
            print(f"  Restored original value")
            
        except Exception as e:
            print(f"✗ Update failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
