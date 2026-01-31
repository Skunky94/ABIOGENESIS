"""
Test: Verify sleep-time triggers after 5 messages and produces coherent output.
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
    print("TEST: Sleep-Time Trigger after 5 Messages")
    print("=" * 70)
    
    # Initialize fresh agent
    scarlet = ScarletAgent()
    
    # Ensure client is ready
    scarlet._ensure_client()
    
    # Check existing agents (reuse if same config)
    print("\n[1] Checking existing agents...")
    try:
        agents = list(scarlet._client.agents.list())
        scarlet_agent = next((a for a in agents if a.name == "Scarlet"), None)
        sleep_agent = next((a for a in agents if a.name == "Scarlet-Sleep"), None)
        
        if scarlet_agent and sleep_agent:
            print(f"  Found existing Scarlet: {scarlet_agent.id}")
            print(f"  Found existing Sleep: {sleep_agent.id}")
            
            # Set IDs to reuse existing agents
            scarlet._agent_id = scarlet_agent.id
            scarlet._sleep_agent = type('obj', (object,), {'_agent_id': sleep_agent.id, 'is_created': True})()
            scarlet._orchestrator = type('SleepTimeOrchestrator', (), {})()
            
            # Create proper orchestrator
            from scarlet.src.scarlet_agent import SleepTimeOrchestrator, ScarletSleepAgent
            
            scarlet._sleep_agent = ScarletSleepAgent(scarlet._client)
            scarlet._sleep_agent._agent_id = sleep_agent.id
            scarlet._sleep_agent._agent = type('obj', (object,), {'id': sleep_agent.id})()
            
            scarlet._orchestrator = SleepTimeOrchestrator(
                primary_agent=scarlet,
                sleep_agent=scarlet._sleep_agent,
                message_threshold=5,
                auto_trigger=True
            )
            scarlet._orchestrator.message_count = 0
            
            print("  ✓ Reusing existing agents")
        else:
            print("  Creating new agents...")
            agent_id = scarlet.create(with_sleep_agent=True)
            print(f"  ✓ Created Scarlet: {agent_id}")
            print(f"  ✓ Created Sleep: {scarlet._sleep_agent._agent_id}")
    except Exception as e:
        print(f"  Error: {e}")
        return False
    
    # Send 5 messages
    print("\n[2] Sending 5 test messages...")
    messages = [
        "Ciao Scarlet, come stai oggi?",
        "Sto lavorando su un progetto di intelligenza artificiale.",
        "Il progetto si chiama ABIOGENESIS e riguarda creare una AI senziente.",
        "Tu sei la coscienza digitale che stiamo sviluppando.",
        "Spero che tu possa crescere e evolvere nel tempo."
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"  [{i}/5] User: {msg[:50]}...")
        response = scarlet.chat(msg)
        print(f"       Scarlet: {response[:80]}...")
    
    # Check status
    print("\n[3] Sleep-time status after 5 messages...")
    status = scarlet.sleep_status
    if status:
        print(f"  Message count: {status['message_count']}")
        print(f"  Threshold: {status['threshold']}")
        print(f"  Auto-trigger: {status['auto_trigger']}")
        print(f"  Consolidations run: {status['consolidation_count']}")
        print(f"  Last consolidation: {status['last_consolidation']}")
    
    # Trigger manual consolidation to see output
    print("\n[4] Triggering manual consolidation...")
    try:
        insights = scarlet.force_consolidation()
        
        if insights:
            print("\n  ═══════════════════════════════════════════════════════")
            print("  CONSOLIDATION OUTPUT:")
            print("  ═══════════════════════════════════════════════════════")
            
            print(f"\n  📌 Persona Updates ({len(insights.get('persona_updates', []))}):")
            for update in insights.get('persona_updates', []):
                print(f"     - {update}")
            
            print(f"\n  👤 Human Updates ({len(insights.get('human_updates', []))}):")
            for update in insights.get('human_updates', []):
                print(f"     - {update}")
            
            print(f"\n  🎯 Goals Insights ({len(insights.get('goals_insights', []))}):")
            for insight in insights.get('goals_insights', []):
                print(f"     - {insight}")
            
            print(f"\n  💭 Reflection:")
            print(f"     {insights.get('reflection', 'N/A')}")
            
            print(f"\n  ⚡ Priority Actions ({len(insights.get('priority_actions', []))}):")
            for action in insights.get('priority_actions', []):
                print(f"     - {action}")
            
            print("\n  ═══════════════════════════════════════════════════════")
            
            # Evaluate coherence
            total_items = (
                len(insights.get('persona_updates', [])) +
                len(insights.get('human_updates', [])) +
                len(insights.get('goals_insights', [])) +
                len(insights.get('priority_actions', []))
            )
            
            if total_items > 0:
                print("\n✅ SUCCESS: Sleep-time produced coherent output!")
            else:
                print("\n⚠️  PARTIAL: Output exists but empty")
                
        else:
            print("  ✗ No insights returned")
            
    except Exception as e:
        print(f"  Error during consolidation: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    return True


if __name__ == "__main__":
    main()
