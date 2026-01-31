"""
Direct API Debug for messages.list
Run: python debug_messages_api.py
"""

from letta_client import Letta

client = Letta(base_url="http://localhost:8283")

AGENT_ID = "agent-e2c4833a-3b3a-4c16-9b7e-8e0230472722"

print("=" * 70)
print("DEBUG MESSAGES LIST API")
print("=" * 70)

print(f"\nAgent ID: {AGENT_ID}")

try:
    print("\nCalling messages.list()...")
    response = client.agents.messages.list(
        agent_id=AGENT_ID,
        limit=10
    )
    
    print(f"\nResponse type: {type(response)}")
    print(f"Response attributes: {dir(response)}")
    
    # Check for messages
    if hasattr(response, 'messages'):
        print(f"\nhasattr(response, 'messages'): True")
        msgs = response.messages
        print(f"  Type: {type(msgs)}")
        print(f"  Count: {len(msgs) if hasattr(msgs, '__len__') else 'unknown'}")
        
        if msgs:
            print(f"\n  First message:")
            first = msgs[0]
            print(f"    Type: {type(first)}")
            print(f"    Attributes: {dir(first)}")
            
            if hasattr(first, 'role'):
                print(f"    role: {first.role}")
            if hasattr(first, 'content'):
                print(f"    content: {first.content}")
    
    elif isinstance(response, dict):
        print(f"\nResponse is dict with keys: {response.keys()}")
        if 'messages' in response:
            msgs = response['messages']
            print(f"  messages count: {len(msgs)}")
    
    else:
        print(f"\nUnexpected response format")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
