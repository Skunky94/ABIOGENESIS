"""
Debug: Check blocks.update signature
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
    print("DEBUG: blocks.update signature")
    print("=" * 70)
    
    scarlet = ScarletAgent()
    scarlet._ensure_client()
    
    # Get blocks.update method info
    update_method = scarlet._client.agents.blocks.update
    print(f"\nMethod: {update_method}")
    print(f"Method type: {type(update_method)}")
    
    # Try to get signature
    import inspect
    try:
        sig = inspect.signature(update_method)
        print(f"Signature: {sig}")
    except Exception as e:
        print(f"Cannot get signature: {e}")
    
    # Check the method's parameters
    try:
        # Try different API styles
        print("\nTrying API variations...")
        
        # Get a block first
        agents = list(scarlet._client.agents.list())
        agent = next((a for a in agents if a.name == "Scarlet"), None)
        
        if agent:
            block = scarlet._client.agents.blocks.retrieve(
                agent_id=agent.id,
                block_label="persona"
            )
            print(f"\nBlock ID: {block.id}")
            print(f"Block attributes: {[a for a in dir(block) if not a.startswith('_')]}")
            
            # Try update with just value
            print("\nTrying update with just value...")
            try:
                # This should work - blocks are identified by their own ID, not with agent_id
                result = scarlet._client.agents.blocks.update(
                    block_id=block.id,
                    value="TEST VALUE"
                )
                print(f"✓ Update worked! Result: {result}")
            except Exception as e:
                print(f"✗ Update failed: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
