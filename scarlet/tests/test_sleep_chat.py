"""
Test Sleep-Time with ScarletAgent.chat()

This test uses the Python API (ScarletAgent.chat()) which properly
triggers the SleepTimeOrchestrator.on_message() mechanism.

Expected flow:
1. ScarletAgent.chat("message") 
2. Sends message to Letta server
3. on_message(1) increments counter
4. After 5 messages, run_consolidation() is called
5. Sleep agent receives conversation for analysis
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from scarlet_agent import ScarletAgent

def test_sleep_with_chat():
    """Test sleep-time activation using ScarletAgent.chat()."""
    print("=" * 70)
    print("TEST: Sleep-Time via ScarletAgent.chat()")
    print("=" * 70)
    
    # Create ScarletAgent - should use EXISTING agents!
    print("\n[1] Creating ScarletAgent...")
    scarlet = ScarletAgent()
    
    # This should use existing agents, not create new ones
    agent_id = scarlet.create(with_sleep_agent=True)
    print(f"  Agent ID: {agent_id}")
    
    # Verify sleep-time is enabled
    print(f"  Sleep enabled: {scarlet.is_sleep_enabled}")
    print(f"  Orchestrator: {scarlet._orchestrator is not None}")
    
    if scarlet.sleep_status:
        print(f"  Threshold: {scarlet.sleep_status['threshold']}")
        print(f"  Message count: {scarlet.sleep_status['message_count']}")
    
    # Test messages to send
    messages = [
        "Ragiona sugli ultimi test, e sul tuo stato",
        "rifletti",
        "rifletti", 
        "rifletti",
        "rifletti"
    ]
    
    print(f"\n[2] Sending {len(messages)} messages via ScarletAgent.chat()...")
    
    for i, msg in enumerate(messages, 1):
        print(f"\n  [{i}.{len(messages)}] '{msg}'")
        
        try:
            response = scarlet.chat(msg)
            print(f"  Response: {response[:150]}...")
            
            # Check sleep status after each message
            if scarlet.sleep_status:
                count = scarlet.sleep_status['message_count']
                threshold = scarlet.sleep_status['threshold']
                print(f"  Sleep status: {count}/{threshold} messages")
                if count >= threshold:
                    print(f"  *** THRESHOLD REACHED! ***")
        
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Final status check
    print(f"\n[3] Final sleep status:")
    if scarlet.sleep_status:
        for k, v in scarlet.sleep_status.items():
            print(f"  {k}: {v}")
    
    # Check consolidation history
    if scarlet._orchestrator:
        print(f"\n[4] Consolidation history:")
        print(f"  Total consolidations: {len(scarlet._orchestrator.consolidation_history)}")
        for i, entry in enumerate(scarlet._orchestrator.consolidation_history):
            print(f"    {i+1}. {entry}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_sleep_with_chat()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
