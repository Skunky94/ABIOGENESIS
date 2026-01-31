#!/usr/bin/env python3
"""
Create or recreate Scarlet agent with complete configuration.
"""
import requests

LETTA_URL = "http://localhost:8283"

def check_existing_agent():
    """Check if Scarlet agent exists."""
    response = requests.get(f"{LETTA_URL}/v1/agents")
    if response.status_code == 200:
        agents = response.json()
        for agent in agents:
            if agent.get('name') == 'Scarlet':
                return agent
    return None

def delete_agent(agent_id):
    """Delete an agent by ID."""
    response = requests.delete(f"{LETTA_URL}/v1/agents/{agent_id}")
    return response.status_code in [200, 204]

def main():
    print("=== Scarlet Agent Manager ===\n")
    
    # Check existing
    existing = check_existing_agent()
    if existing:
        print(f"Found existing agent: {existing['id']}")
        print(f"  - Type: {existing.get('agent_type', 'unknown')}")
        print(f"  - Sleep-time: {existing.get('enable_sleeptime', False)}")
        print(f"  - Context window: {existing.get('llm_config', {}).get('context_window', 'unknown')}")
        
        choice = input("\nDelete and recreate? (yes/no): ")
        if choice.lower() == 'yes':
            print("\nDeleting existing agent...")
            if delete_agent(existing['id']):
                print("✓ Agent deleted")
            else:
                print("✗ Failed to delete agent")
                return
    else:
        print("No existing Scarlet agent found")
    
    # Import and create new agent
    print("\nCreating new agent with complete configuration...")
    try:
        from scarlet_agent import ScarletAgent
        agent_id = ScarletAgent().create()
        print(f"✓ Agent created: {agent_id}")
        
        # Verify
        response = requests.get(f"{LETTA_URL}/v1/agents/{agent_id}")
        if response.status_code == 200:
            agent = response.json()
            print(f"\nVerification:")
            print(f"  - Name: {agent['name']}")
            print(f"  - Type: {agent.get('agent_type')}")
            print(f"  - Model: {agent['model']}")
            print(f"  - Sleep-time: {agent.get('enable_sleeptime')}")
            print(f"  - Context window: {agent.get('llm_config', {}).get('context_window')}")
            print(f"  - Embedding: {agent.get('embedding')}")
            print(f"  - Memory blocks: {len(agent.get('memory', {}).get('blocks', []))}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()
