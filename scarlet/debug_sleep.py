"""
Debug sleep-time consolidation to see actual response.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from scarlet.src.scarlet_agent import ScarletAgent, SleepTimeOrchestrator, ScarletSleepAgent


def main():
    print("=" * 70)
    print("DEBUG: Sleep-Time Consolidation")
    print("=" * 70)
    
    scarlet = ScarletAgent()
    scarlet._ensure_client()
    
    # Find existing agents
    agents = list(scarlet._client.agents.list())
    scarlet_agent = next((a for a in agents if a.name == "Scarlet"), None)
    sleep_agent = next((a for a in agents if a.name == "Scarlet-Sleep"), None)
    
    if not scarlet_agent or not sleep_agent:
        print("ERROR: Agents not found")
        return
    
    print(f"\nUsing Scarlet: {scarlet_agent.id}")
    print(f"Using Sleep: {sleep_agent.id}")
    
    # Setup sleep agent
    sleep_agent_instance = ScarletSleepAgent(scarlet._client)
    sleep_agent_instance._agent_id = sleep_agent.id
    sleep_agent_instance._agent = type('obj', (object,), {'id': sleep_agent.id})()
    
    # Get messages
    print("\n[1] Fetching recent messages...")
    try:
        response = scarlet._client.agents.messages.list(
            agent_id=scarlet_agent.id,
            limit=20
        )
        print(f"  Response type: {type(response)}")
        print(f"  Response: {response}")
        
        if isinstance(response, dict):
            messages = response.get("messages", [])
        elif hasattr(response, 'messages'):
            messages = response.messages
        else:
            messages = list(response) if response else []
        
        print(f"  Found {len(messages)} messages")
        
        # Format messages
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown") if isinstance(msg, dict) else getattr(msg, 'role', 'unknown')
            content = msg.get("content", "")[:300] if isinstance(msg, dict) else getattr(msg, 'content', '')[:300]
            timestamp = msg.get("created_at", "")[:10] if isinstance(msg, dict) else ""
            formatted.append(f"[{timestamp}] {role}: {content}")
        
        conversation_history = "\n".join(formatted)
        print(f"\n[2] Conversation history preview:")
        print("-" * 60)
        print(conversation_history[:500])
        print("-" * 60)
        
        # Test consolidation
        print("\n[3] Testing consolidation directly...")
        
        # Format the prompt
        system_prompt = sleep_agent_instance._load_system_prompt()
        formatted_prompt = system_prompt.format(conversation_history=conversation_history)
        
        print(f"  Prompt length: {len(formatted_prompt)} chars")
        
        # Send to sleep agent
        response = scarlet._client.agents.messages.create(
            agent_id=sleep_agent.id,
            messages=[{"role": "user", "content": formatted_prompt}]
        )
        
        print(f"\n  Response type: {type(response)}")
        
        # Extract response text
        response_text = ""
        if hasattr(response, 'messages') and response.messages:
            msg = response.messages[0]
            print(f"  Message type: {type(msg)}")
            print(f"  Message attributes: {dir(msg)}")
            
            if hasattr(msg, 'content') and msg.content:
                response_text = msg.content
            elif hasattr(msg, 'assistant_message') and msg.assistant_message:
                response_text = msg.assistant_message
        
        print(f"\n  Response text ({len(response_text)} chars):")
        print("-" * 60)
        print(response_text)
        print("-" * 60)
        
        # Try to parse
        print("\n[4] Attempting JSON parse...")
        try:
            import json
            # Clean up
            text = response_text.strip()
            if text.startswith("```json"):
                text = "\n".join(text.split("\n")[1:-1])
            elif text.startswith("```"):
                text = "\n".join(text.split("\n")[1:-1])
            
            start = text.find("{")
            end = text.rfind("}") + 1
            
            if start != -1 and end > 0:
                json_text = text[start:end]
                print(f"  Extracted JSON: {json_text[:200]}...")
                data = json.loads(json_text)
                print(f"  ✓ Parsed successfully!")
                print(f"  Keys: {list(data.keys())}")
            else:
                print("  ✗ No JSON object found")
                
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parse error: {e}")
            print(f"  Position: {e.pos}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
