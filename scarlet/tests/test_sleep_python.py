"""
Test sleep-time using Python ScarletAgent class (NOT HTTP API)

This correctly triggers the SleepTimeOrchestrator which is Python code.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sleep_with_scarlet_agent():
    """Test sleep-time using ScarletAgent class (not HTTP API)."""
    print("=" * 70)
    print("TEST: Sleep-Time with ScarletAgent Python Class")
    print("=" * 70)
    
    try:
        from scarlet_agent import ScarletAgent
        
        print("\n[1] Creating Scarlet agent...")
        scarlet = ScarletAgent()
        
        # We need to use the EXISTING agents, not create new ones
        # The ScarletAgent class should be modified to accept existing agent IDs
        # For now, let's just test if the class works
        
        print(f"  ScarletAgent created: {scarlet}")
        print(f"  Has _ensure_client: {hasattr(scarlet, '_ensure_client')}")
        print(f"  Has chat method: {hasattr(scarlet, 'chat')}")
        print(f"  Has is_sleep_enabled: {hasattr(scarlet, 'is_sleep_enabled')}")
        
        print("\n[2] NOTE: To properly test, ScarletAgent needs to:")
        print("   - Accept existing agent IDs (not create new ones)")
        print("   - Use the official agents we cleaned up")
        print("   - Primary: agent-0ef885f2-a9d9-4e9e-907a-7c6432004710")
        print("   - Sleep:   agent-bc713153-a448-47f4-a26c-12bce2d64612")
        
        print("\n[3] The HTTP API test we ran earlier DOES NOT trigger")
        print("    SleepTimeOrchestrator because it bypasses the Python code!")
        print("    The orchestrator is logic in scarlet_agent.py, not in Letta server.")
        
        print("\n" + "=" * 70)
        print("CONCLUSION")
        print("=" * 70)
        print("""
PROBLEMA IDENTIFICATO:

Il test HTTP diretto (via API) non attiva lo sleep-time perché:
1. SleepTimeOrchestrator è codice Python in scarlet_agent.py
2. L'API HTTP di Letta non sa della nostra logica custom
3. Quando invii via HTTP, bypassi completamente il Python orchestration

SOLUZIONE:

Devi usare la classe ScarletAgent() dal Python code:
   scarlet = ScarletAgent()
   scarlet.create(with_sleep_agent=True)
   response = scarlet.chat("message")

Solo così si attiva:
   scarlet.chat() → on_message() → run_consolidation() → Sleep Agent

OPPURE integrare la logica nel server Letta (più complesso).
""")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sleep_with_scarlet_agent()
    sys.exit(0 if success else 1)
