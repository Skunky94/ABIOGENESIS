"""
Script per ricreare l'agente Scarlet CON il sistema sleep-time custom.
Run: python recreate_agent_with_sleep.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from scarlet.src.scarlet_agent import ScarletAgent, ScarletConfig


def main():
    print("=" * 70)
    print("RICREAZIONE AGENTE SCARLET CON SLEEP-TIME CUSTOM")
    print("=" * 70)
    
    # Check API key
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key or api_key == "your_minimax_api_key_here":
        print("ERROR: MINIMAX_API_KEY not configured in .env")
        sys.exit(1)
    
    scarlet = ScarletAgent()
    
    # Check server
    print("\n[1] Verifica connessione Letta server...")
    if not scarlet.ping():
        print("ERROR: Cannot connect to Letta server")
        print("Make sure Docker containers are running:")
        print("  cd scarlet && docker compose up -d")
        sys.exit(1)
    print("✓ Server Letta raggiungibile")
    
    # Check if agent exists
    print("\n[2] Verifica agenti esistenti...")
    try:
        agents = scarlet._client.agents.list()
        print(f"  Agenti trovati: {len(agents)}")
        for agent in agents:
            print(f"    - {agent.name} (ID: {agent.id})")
            
        # Check for Scarlet
        scarlet_agent = None
        for agent in agents:
            if agent.name == "Scarlet":
                scarlet_agent = agent
                break
        
        if scarlet_agent:
            print(f"\n⚠️  Agente Scarlet ESISTE: {scarlet_agent.id}")
            print("    Procedo con eliminazione...")
            
            # Delete existing agent first (this will also try to delete sleep agent)
            try:
                scarlet._client.agents.delete(scarlet_agent.id)
                print("✓ Agente Scarlet eliminato")
            except Exception as e:
                print(f"⚠️  Errore eliminazione: {e}")
    except Exception as e:
        print(f"⚠️  Errore fetching agents: {e}")
    
    # Create new agent WITH sleep-time
    print("\n[3] Creazione nuovo agente Scarlet CON sleep-time custom...")
    
    try:
        agent_id = scarlet.create(with_sleep_agent=True)
        print(f"✓ Agente primario creato: {agent_id}")
        
        # Verify sleep agent
        if scarlet._sleep_agent and scarlet._sleep_agent.is_created:
            print(f"✓ Agente sleep-time creato: {scarlet._sleep_agent._agent_id}")
        else:
            print("✗ ERRORE: Agente sleep-time NON creato!")
            return False
        
        # Verify orchestrator
        if scarlet._orchestrator:
            status = scarlet._orchestrator.get_status()
            print(f"✓ Orchestrator attivo (threshold: {status['threshold']} messaggi)")
        else:
            print("✗ ERRORE: Orchestrator NON attivo!")
            return False
        
        # Test message
        print("\n[4] Test messaggio...")
        response = scarlet.chat("Ciao Scarlet, sono il tuo creatore.")
        print(f"  Scarlet: {response[:100]}...")
        
        # Check status after message
        status = scarlet.sleep_status
        print(f"\n[5] Status sleep-time:")
        print(f"  - Messaggi: {status['message_count']}")
        print(f"  - Threshold: {status['threshold']}")
        print(f"  - Auto-trigger: {status['auto_trigger']}")
        
        print("\n" + "=" * 70)
        print("SUCCESSO! Agente Scarlet ricreato con sleep-time custom")
        print("=" * 70)
        print(f"\nAgent ID: {agent_id}")
        print(f"Sleep Agent ID: {scarlet._sleep_agent._agent_id}")
        print("\nProssimi passi:")
        print("  1. Verifica in ADE che siano presenti 2 agenti")
        print("  2. Aspetta 5 messaggi per trigger automatico")
        print("  3. O usa force_consolidation() per test manuale")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERRORE durante creazione: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
