"""
Test consolidazione con gli agenti esistenti (ID fissi)
Run: python test_consolidation_fixed.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from letta_client import Letta


# ID degli agenti appena creati
PRIMARY_AGENT_ID = "agent-e2c4833a-3b3a-4c16-9b7e-8e0230472722"
SLEEP_AGENT_ID = "agent-eb908ad7-4384-4929-8612-208b23e57f72"


def test_consolidation():
    print("=" * 70)
    print("TEST CONSOLIDAZIONE")
    print("=" * 70)
    
    # Connect
    client = Letta(
        base_url="http://localhost:8283",
        api_key=os.getenv("MINIMAX_API_KEY")
    )
    
    # Step 1: Get recent messages
    print("\n[1] Recupero messaggi recenti...")
    try:
        response = client.agents.messages.list(
            agent_id=PRIMARY_AGENT_ID,
            limit=20
        )
        print(f"  Response type: {type(response)}")
        
        # Try to extract messages
        messages = []
        if hasattr(response, 'messages'):
            messages = response.messages
        elif isinstance(response, dict):
            messages = response.get("messages", [])
        elif hasattr(response, '__iter__'):
            # It might be a list
            messages = list(response)
        
        print(f"  Messaggi estratti: {len(messages)}")
        
        if messages:
            print(f"\n  Primi 3 messaggi:")
            for i, msg in enumerate(messages[:3]):
                print(f"\n  Messaggio {i+1}:")
                print(f"    Type: {type(msg)}")
                if hasattr(msg, 'role'):
                    print(f"    Role: {msg.role}")
                if hasattr(msg, 'content'):
                    content = msg.content
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"    Content: {content}")
                # Also try dict format
                if isinstance(msg, dict):
                    print(f"    Dict keys: {msg.keys()}")
        else:
            print("  ⚠️  Nessun messaggio trovato!")
            
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Send to sleep agent
    print("\n" + "-" * 70)
    print("\n[2] Invio a sleep agent per consolidamento...")
    
    prompt = f"""Analizza questa cronologia e genera insights JSON:

Cronologia:
{str(messages)[:2000]}

Rispondi SOLO con JSON:
{{{{
    "persona_updates": ["nuovo insight 1"],
    "human_updates": ["info sull'umano"],
    "goals_insights": ["progresso verso obiettivi"],
    "reflection": "riflessione breve",
    "priority_actions": ["azione importante"]
}}}}"""

    try:
        response = client.agents.messages.create(
            agent_id=SLEEP_AGENT_ID,
            messages=[{"role": "user", "content": prompt}]
        )
        
        print(f"  Response type: {type(response)}")
        
        # Extract response text
        response_text = ""
        if hasattr(response, 'messages') and response.messages:
            msg = response.messages[0]
            if hasattr(msg, 'content') and msg.content:
                response_text = msg.content
            elif hasattr(msg, 'assistant_message') and msg.assistant_message:
                response_text = msg.assistant_message
        elif hasattr(response, 'assistant_message') and response.assistant_message:
            response_text = response.assistant_message
        elif isinstance(response, str):
            response_text = response
        
        print(f"\n  Risposta grezza ({len(response_text)} chars):")
        print("-" * 60)
        print(response_text[:500] if len(response_text) > 500 else response_text)
        print("-" * 60)
        
        # Try to parse JSON
        import json
        try:
            # Clean markdown code blocks
            text = response_text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                json_text = text[start:end+1]
                insights = json.loads(json_text)
                print(f"\n✓ JSON parsato correttamente:")
                print(json.dumps(insights, indent=2, ensure_ascii=False))
            else:
                print("\n⚠️  Nessun JSON trovato nella risposta")
        except json.JSONDecodeError as e:
            print(f"\n✗ Errore parsing JSON: {e}")
            
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("TEST COMPLETATO")
    print("=" * 70)


if __name__ == "__main__":
    test_consolidation()
