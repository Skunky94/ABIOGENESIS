#!/usr/bin/env python3
"""
Test agent creation with minimal config.
"""
import requests

LETTA_URL = "http://localhost:8283"

def test_simple():
    """Test with minimal config."""
    print("=== Test 1: Minimal Config ===")
    
    # Read system prompt
    with open("prompts/system.txt", "r") as f:
        system_prompt = f.read()
    
    # Simple memory blocks
    memory_blocks = [
        {"label": "persona", "value": "Tu sei Scarlet.", "limit": 5000},
        {"label": "human", "value": "Informazioni sull'umano.", "limit": 5000},
    ]
    
    create_params = {
        "name": "Scarlet",
        "system": system_prompt,
        "model": "minimax/MiniMax-M2.1",
        "memory_blocks": memory_blocks
    }
    
    print(f"Sending request to {LETTA_URL}/v1/agents...")
    response = requests.post(
        f"{LETTA_URL}/v1/agents",
        json=create_params,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        agent = response.json()
        print(f"✓ Agent created: {agent['id']}")
        print(f"  Type: {agent.get('agent_type')}")
        print(f"  Model: {agent['model']}")
        print(f"  Sleep-time: {agent.get('enable_sleeptime')}")
        print(f"  Memory blocks: {len(agent.get('memory', {}).get('blocks', []))}")
        return agent['id']
    else:
        print(f"✗ Error: {response.text[:500]}")
        return None

def test_with_context():
    """Test with context window."""
    print("\n=== Test 2: With Context Window ===")
    
    with open("prompts/system.txt", "r") as f:
        system_prompt = f.read()
    
    memory_blocks = [
        {"label": "persona", "value": "Tu sei Scarlet.", "limit": 5000},
        {"label": "human", "value": "Informazioni sull'umano.", "limit": 5000},
    ]
    
    create_params = {
        "name": "Scarlet",
        "system": system_prompt,
        "model": "minimax/MiniMax-M2.1",
        "context_window_limit": 200000,
        "memory_blocks": memory_blocks
    }
    
    response = requests.post(
        f"{LETTA_URL}/v1/agents",
        json=create_params,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"✓ Agent created with context window")
        return response.json()['id']
    else:
        print(f"✗ Error: {response.text[:500]}")
        return None

def test_with_sleeptime():
    """Test with sleep-time."""
    print("\n=== Test 3: With Sleep-Time ===")
    
    with open("prompts/system.txt", "r") as f:
        system_prompt = f.read()
    
    memory_blocks = [
        {"label": "persona", "value": "Tu sei Scarlet.", "limit": 5000},
        {"label": "human", "value": "Informazioni sull'umano.", "limit": 5000},
    ]
    
    create_params = {
        "name": "Scarlet",
        "system": system_prompt,
        "model": "minimax/MiniMax-M2.1",
        "enable_sleeptime": True,
        "memory_blocks": memory_blocks
    }
    
    response = requests.post(
        f"{LETTA_URL}/v1/agents",
        json=create_params,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"✓ Agent created with sleep-time")
        return response.json()['id']
    else:
        print(f"✗ Error: {response.text[:500]}")
        return None

def cleanup(agent_id):
    """Delete test agent."""
    if agent_id:
        requests.delete(f"{LETTA_URL}/v1/agents/{agent_id}")
        print(f"\nCleaned up agent: {agent_id}")

if __name__ == "__main__":
    # Test 1: Minimal
    agent1 = test_simple()
    
    if agent1:
        cleanup(agent1)
        
        # Test 2: With context
        agent2 = test_with_context()
        
        if agent2:
            cleanup(agent2)
            
            # Test 3: With sleep-time
            agent3 = test_with_sleeptime()
            
            if agent3:
                print("\n✓ Test 3 passed - use this config!")
            else:
                print("\n✗ Sleep-time causes issues")
    else:
        print("\n✗ Minimal config failed - check Letta server")
