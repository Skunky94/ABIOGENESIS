"""
Pulisce agenti vecchi lasciando solo gli ultimi 2 (1 Scarlet + 1 Sleeping)
Run: python cleanup_agents.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from scarlet.src.scarlet_agent import ScarletAgent


def main():
    print("=" * 70)
    print("PULIZIA AGENTI VECCHI")
    print("=" * 70)
    
    scarlet = ScarletAgent()
    
    # Check server
    if not scarlet.ping():
        print("ERROR: Cannot connect to Letta server")
        sys.exit(1)
    
    # Get all agents
    print("\n[1] Recupero lista agenti...")
    try:
        agents = list(scarlet._client.agents.list())
        print(f"  Totale agenti: {len(agents)}")
        
        # Print all agents with details
        print("\n[2] Agenti trovati:")
        agent_info = []
        for agent in agents:
            created_at = getattr(agent, 'created_at', None)
            created_str = created_at.isoformat() if created_at else "Unknown"
            agent_info.append({
                'id': agent.id,
                'name': agent.name,
                'created_at': created_at,
                'created_str': created_str
            })
            print(f"  - {agent.name} ({agent.id})")
            print(f"    Creato: {created_str}")
        
        # Sort by creation date (newest first)
        agent_info.sort(key=lambda x: x['created_at'] or datetime.min, reverse=True)
        
        # Identify keepers (1 Scarlet, 1 Sleeping newest)
        keepers = []
        scarlet_kept = False
        sleeping_kept = False
        
        for agent in agent_info:
            if agent['name'] == 'Scarlet' and not scarlet_kept:
                keepers.append(agent['id'])
                scarlet_kept = True
                print(f"\n[3] KEEPER - Scarlet (più recente): {agent['id']}")
            elif 'Sleep' in agent['name'] and not sleeping_kept:
                keepers.append(agent['id'])
                sleeping_kept = True
                print(f"\n[3] KEEPER - Sleep (più recente): {agent['id']}")
        
        print(f"\n[4] Da eliminare: {len(agents) - len(keepers)} agenti")
        
        # Delete old agents
        deleted = []
        for agent in agent_info:
            if agent['id'] not in keepers:
                try:
                    scarlet._client.agents.delete(agent['id'])
                    deleted.append(agent['name'])
                    print(f"  ✗ Eliminato: {agent['name']} ({agent['id']})")
                except Exception as e:
                    print(f"  ⚠️  Errore eliminando {agent['name']}: {e}")
        
        print(f"\n[5] RISULTATO:")
        print(f"  Eliminati: {len(deleted)}")
        print(f"  Keeper IDs: {keepers}")
        
        # Verify remaining
        remaining = list(scarlet._client.agents.list())
        print(f"\n[6] Agenti rimanenti ({len(remaining)}):")
        for agent in remaining:
            print(f"  - {agent.name} ({agent.id})")
        
        print("\n" + "=" * 70)
        print("PULIZIA COMPLETATA!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
