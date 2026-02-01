"""
Test retrieval automatico con Scarlet.
Invia un messaggio e verifica che il retrieval funzioni.
"""

import requests
import time

LETTA_URL = "http://localhost:8283"
SCARLET_AGENT_ID = "agent-ac26cf86-3890-40a9-a70f-967f05115da9"

def send_message(message: str) -> dict:
    """Send a message to Scarlet via Letta API."""
    resp = requests.post(
        f"{LETTA_URL}/v1/agents/{SCARLET_AGENT_ID}/messages",
        headers={"Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "user", "content": message}
            ]
        }
    )
    return resp.json()

def get_session_context() -> str:
    """Get current session_context from Scarlet."""
    resp = requests.get(f"{LETTA_URL}/v1/agents/{SCARLET_AGENT_ID}/core-memory")
    data = resp.json()
    blocks = data.get("blocks", []) if isinstance(data, dict) else data
    for block in blocks:
        if block.get("label") == "session_context":
            return block.get("value", "")
    return ""

def main():
    print("="*60)
    print("TEST RETRIEVAL AUTOMATICO")
    print("="*60)
    
    # Test message that should trigger relevant memory retrieval
    test_message = "Ciao Scarlet! Ricordi chi sono e cosa stiamo sviluppando insieme?"
    
    print(f"\n📤 Invio messaggio: '{test_message}'")
    print("   (Il webhook dovrebbe fare retrieval automatico)")
    print()
    
    # Send message
    response = send_message(test_message)
    
    # Wait a moment for webhook to process
    time.sleep(2)
    
    # Check session_context
    session = get_session_context()
    
    print("="*60)
    print("📝 SESSION_CONTEXT ATTUALE:")
    print("="*60)
    print(session[:2000] if len(session) > 2000 else session)
    
    print("\n" + "="*60)
    print("💬 RISPOSTA SCARLET:")
    print("="*60)
    
    for msg in response:
        if msg.get("message_type") == "assistant_message":
            content = msg.get("content", "")
            print(content[:500] if len(content) > 500 else content)

if __name__ == "__main__":
    main()
