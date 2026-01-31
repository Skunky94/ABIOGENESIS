"""
Script per pulire e ricreare gli agenti con il nuovo prompt dedicato per lo sleeping.
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
    print("PULIZIA E RICREAZIONE AGENTI CON NUOVO PROMPT SLEEPING")
    print("=" * 70)
    
    scarlet = ScarletAgent()
    
    # Check server
    print("\n[1] Verifica server...")
    if not scarlet.ping():
        print("ERROR: Cannot connect to Letta server")
        sys.exit(1)
    print("✓ Server OK")
    
    # Get all agents
    print("\n[2] Lista agenti esistenti...")
    try:
        agents = list(scarlet._client.agents.list())
        print(f"  Trovati {len(agents)} agenti")
        
        scarlet_agents = [a for a in agents if a.name == "Scarlet"]
        sleep_agents = [a for a in agents if a.name == "Scarlet-Sleep"]
        
        print(f"  Scarlet: {len(scarlet_agents)}")
        print(f"  Scarlet-Sleep: {len(sleep_agents)}")
        
        # Delete all Scarlet agents
        print("\n[3] Eliminazione agenti Scarlet...")
        for agent in scarlet_agents:
            try:
                scarlet._client.agents.delete(agent.id)
                print(f"  ✓ Eliminato: {agent.id}")
            except Exception as e:
                print(f"  ✗ Errore: {e}")
        
        # Delete all Sleep agents
        print("\n[4] Eliminazione agenti Scarlet-Sleep...")
        for agent in sleep_agents:
            try:
                scarlet._client.agents.delete(agent.id)
                print(f"  ✓ Eliminato: {agent.id}")
            except Exception as e:
                print(f"  ✗ Errore: {e}")
                
    except Exception as e:
        print(f"  ⚠️  Errore fetching agents: {e}")
    
    # Create new agents
    print("\n[5] Creazione nuovi agenti...")
    try:
        agent_id = scarlet.create(with_sleep_agent=True)
        print(f"✓ Scarlet creato: {agent_id}")
        print(f"✓ Scarlet-Sleep creato: {scarlet._sleep_agent._agent_id}")
        
        # Verify prompts
        print("\n[6] Verifica prompt dedicati...")
        print(f"  Scarlet: usa {scarlet.config.system_prompt_path}")
        print(f"  Scarlet-Sleep: usa prompts/system_sleep.txt")
        
        print("\n" + "=" * 70)
        print("SUCCESSO! Agenti ricreati con prompt separati")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n✗ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
