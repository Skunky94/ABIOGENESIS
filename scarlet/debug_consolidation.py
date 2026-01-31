"""
Debug Sleep-Time Consolidation
Run: python debug_consolidation.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from scarlet.src.scarlet_agent import ScarletAgent, ScarletSleepAgent


def main():
    print("=" * 70)
    print("DEBUG SLEEP-TIME CONSOLIDATION")
    print("=" * 70)
    
    # Use existing agent IDs from previous run
    # Use agent IDs from most recent run (test_consolidation.py)
    PRIMARY_AGENT_ID = "agent-e2c4833a-3b3a-4c16-9b7e-8e0230472722"  # Scarlet (most recent)
    SLEEP_AGENT_ID = "agent-eb908ad7-4384-4929-8612-208b23e57f72"    # Scarlet-Sleep (most recent)
    
    print(f"  Using Primary Agent: {PRIMARY_AGENT_ID}")
    print(f"  Using Sleep Agent: {SLEEP_AGENT_ID}")
    
    scarlet = ScarletAgent()
    scarlet._ensure_client()
    
    # Set agent IDs manually
    scarlet._agent_id = PRIMARY_AGENT_ID
    
    # Create or reuse sleep agent
    if not scarlet._sleep_agent:
        from scarlet.src.scarlet_agent import ScarletSleepAgent
        scarlet._sleep_agent = ScarletSleepAgent(client=scarlet._client)
        scarlet._sleep_agent._agent_id = SLEEP_AGENT_ID
        print(f"  Sleep agent reference set: {scarlet._sleep_agent._agent_id}")
    
    # Get recent messages (simulate orchestrator)
    print("\n[1] Recupero messaggi recenti...")
    try:
        response = scarlet._client.agents.messages.list(
            agent_id=scarlet._agent_id,
            limit=50
        )
        print(f"  Tipo risposta: {type(response)}")
        
        # Try to access messages
        if hasattr(response, 'messages'):
            messages = response.messages
            print(f"  Messaggi (direct): {len(messages)}")
        elif isinstance(response, dict) and 'messages' in response:
            messages = response['messages']
            print(f"  Messaggi (dict): {len(messages)}")
        else:
            print(f"  Attributi disponibili: {dir(response)}")
            messages = []
        
        # Format messages
        print(f"\n  Primi 3 messaggi formattati:")
        formatted = []
        for msg in messages[-10:]:  # Last 10
            role = getattr(msg, 'role', 'unknown') if hasattr(msg, 'role') else msg.get('role', 'unknown')
            content = getattr(msg, 'content', '') or getattr(msg, 'assistant_message', '')
            if hasattr(content, 'value'):
                content = content.value
            content = str(content)[:300]
            formatted.append(f"[{role}]: {content}")
            print(f"    {formatted[-1]}")
        
        conversation_text = "\n".join(formatted)
        
    except Exception as e:
        print(f"  ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test sleep agent directly
    print("\n" + "=" * 70)
    print("[2] Test Sleep Agent Direttamente")
    print("=" * 70)
    
    if not scarlet._sleep_agent:
        print("  Creando sleep agent...")
        scarlet._sleep_agent = ScarletSleepAgent(
            client=scarlet._client
        )
    
    if not scarlet._sleep_agent.is_created:
        print("  Creando sleep agent in Letta...")
        with open(Path(__file__).parent / "prompts" / "system.txt", 'r') as f:
            system_prompt = f.read()
        scarlet._sleep_agent.create(system_prompt)
        print(f"  Sleep agent creato: {scarlet._sleep_agent._agent_id}")
    
    # Send consolidation prompt
    print("\n[3] Invio prompt consolidazione...")
    prompt = scarlet._sleep_agent.PROMPT_TEMPLATE.format(
        conversation_history=conversation_text
    )
    print(f"  Prompt length: {len(prompt)} chars")
    
    try:
        response = scarlet._sleep_agent.client.agents.messages.create(
            agent_id=scarlet._sleep_agent._agent_id,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract response
        response_text = ""
        if hasattr(response, 'messages') and response.messages:
            msg = response.messages[0]
            response_text = getattr(msg, 'content', '') or getattr(msg, 'assistant_message', '')
            if hasattr(response_text, 'value'):
                response_text = response_text.value
            response_text = str(response_text)
        
        print(f"  Response length: {len(response_text)} chars")
        print(f"\n  RISPOSTA COMPLETA:")
        print("-" * 70)
        print(response_text[:2000])
        print("-" * 70)
        
        # Parse JSON
        print("\n[4] Parsing JSON...")
        insights = scarlet._sleep_agent._parse_insights(response_text)
        print(f"  Insights parsed: {insights}")
        
    except Exception as e:
        print(f"  ERRORE: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
