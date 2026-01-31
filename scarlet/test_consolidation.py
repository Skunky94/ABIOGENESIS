"""
Test Sleep-Time Consolidation
Run: python test_consolidation.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from scarlet.src.scarlet_agent import ScarletAgent


def main():
    print("=" * 70)
    print("TEST SLEEP-TIME CONSOLIDATION")
    print("=" * 70)
    
    scarlet = ScarletAgent()
    
    # Check server
    print("\n[1] Verifica connessione Letta server...")
    if not scarlet.ping():
        print("ERROR: Cannot connect to Letta server")
        sys.exit(1)
    print("✓ Server OK")
    
    # Get agent info
    print("\n[2] Agenti configurati:")
    print(f"  Primary: {scarlet._agent_id if scarlet.is_created else 'Non creato'}")
    if scarlet._sleep_agent:
        print(f"  Sleep:   {scarlet._sleep_agent._agent_id if scarlet._sleep_agent.is_created else 'Non creato'}")
    
    # Send messages to accumulate messages
    print("\n[3] Invio messaggi per accumulare conversazione...")
    messages = [
        "Ciao Scarlet, oggi è una bella giornata",
        "Sto lavorando al progetto ABIOGENESIS",
        "Abbiamo implementato il sistema sleep-time custom",
        "Ora testiamo la consolidazione della memoria",
        "Questo è il quinto messaggio"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n  [{i}/5] User: {msg}")
        response = scarlet.chat(msg)
        print(f"  Scarlet: {response[:150]}...")
    
    # Check status
    print("\n[4] Status sleep-time:")
    status = scarlet.sleep_status
    print(f"  - Message count: {status['message_count']}")
    print(f"  - Threshold: {status['threshold']}")
    print(f"  - Consolidations run: {status['consolidation_count']}")
    
    # Force consolidation
    print("\n[5] Trigger consolidazione manuale...")
    print("  Chiamando force_consolidation()...")
    
    try:
        insights = scarlet.force_consolidation()
        
        print("\n✓ Consolidazione completata!")
        print("\n" + "=" * 70)
        print("INSIGHTS RESTITUITI:")
        print("=" * 70)
        
        print(f"\nPersona Updates ({len(insights.get('persona_updates', []))}):")
        for update in insights.get('persona_updates', []):
            print(f"  • {update}")
        
        print(f"\nHuman Updates ({len(insights.get('human_updates', []))}):")
        for update in insights.get('human_updates', []):
            print(f"  • {update}")
        
        print(f"\nGoals Insights ({len(insights.get('goals_insights', []))}):")
        for insight in insights.get('goals_insights', []):
            print(f"  • {insight}")
        
        print(f"\nReflection:")
        print(f"  {insights.get('reflection', 'N/A')}")
        
        print(f"\nPriority Actions ({len(insights.get('priority_actions', []))}):")
        for action in insights.get('priority_actions', []):
            print(f"  • {action}")
        
        # Check updated status
        print("\n" + "=" * 70)
        print("STATO DOPO CONSOLIDAZIONE:")
        print("=" * 70)
        status = scarlet.sleep_status
        print(f"  - Message count: {status['message_count']}")
        print(f"  - Threshold: {status['threshold']}")
        print(f"  - Consolidations run: {status['consolidation_count']}")
        print(f"  - Last consolidation: {status['last_consolidation']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERRORE durante consolidazione: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
