#!/usr/bin/env python3
"""Test script to enable sleep-time on Scarlet agent"""

import requests
import json

AGENT_ID = "agent-ed8a8d29-75eb-4543-b4f7-59745589c07c"
LETTA_URL = "http://localhost:8283"

# Test current agent state
print("=== Current Agent State ===")
response = requests.get(f"{LETTA_URL}/v1/agents/{AGENT_ID}")
print(f"Status: {response.status_code}")
agent = response.json()
print(f"Name: {agent['name']}")
print(f"Enable Sleep-time: {agent.get('enable_sleeptime')}")
print(f"Has managed_group: {agent.get('managed_group') is not None}")

# Try to enable sleep-time
print("\n=== Enabling Sleep-time ===")
update_data = {"enable_sleeptime": True}
response = requests.patch(
    f"{LETTA_URL}/v1/agents/{AGENT_ID}",
    json=update_data,
    headers={"Content-Type": "application/json"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Verify
print("\n=== Verification ===")
response = requests.get(f"{LETTA_URL}/v1/agents/{AGENT_ID}")
agent = response.json()
print(f"Enable Sleep-time after update: {agent.get('enable_sleeptime')}")
print(f"Has managed_group: {agent.get('managed_group') is not None}")
