#!/usr/bin/env python3
"""Check sleep-time agent creation"""

import requests

AGENT_ID = "agent-ed8a8d29-75eb-4543-b4f7-59745589c07c"
LETTA_URL = "http://localhost:8283"

# Get full agent state
print("=== Full Agent State ===")
response = requests.get(f"{LETTA_URL}/v1/agents/{AGENT_ID}")
agent = response.json()

print(f"ID: {agent['id']}")
print(f"Name: {agent['name']}")
print(f"Enable Sleep-time: {agent.get('enable_sleeptime')}")
print(f"Managed Group: {agent.get('managed_group')}")
print(f"Agent Type: {agent.get('agent_type')}")

# Check if there are any groups
print("\n=== Checking Groups ===")
response = requests.get(f"{LETTA_URL}/v1/groups")
print(f"Groups status: {response.status_code}")
if response.status_code == 200:
    groups = response.json()
    print(f"Total groups: {len(groups)}")
    for g in groups:
        print(f"  - {g.get('id', 'N/A')}: {g.get('name', 'N/A')}")

# Check tools - should include sleep-time tools
print("\n=== Checking Sleep-time Tools ===")
tools = agent.get('tools', [])
sleep_tools = [t for t in tools if 'sleeptime' in t.get('tags', [])]
print(f"Sleep-time tools count: {len(sleep_tools)}")
for t in sleep_tools:
    print(f"  - {t['name']} (type: {t['tool_type']})")

# Try to trigger a sleep-time cycle by sending a message
print("\n=== Triggering Interaction ===")
# Just check - don't actually send a message
print("To trigger sleep-time, interact with Scarlet or check managed_group after a few messages")
