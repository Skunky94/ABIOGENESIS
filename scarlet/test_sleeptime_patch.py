#!/usr/bin/env python3
"""Test enabling sleep-time after agent creation."""
import requests

LETTA_URL = "http://localhost:8283"
AGENT_ID = "agent-c8f46fe6-9011-4d71-b267-10c7808ba02f"

print("=== Test: Enable Sleep-Time via PATCH ===\n")

# Check current state
response = requests.get(f"{LETTA_URL}/v1/agents/{AGENT_ID}")
agent = response.json()
print(f"Before PATCH:")
print(f"  Enable sleep-time: {agent.get('enable_sleeptime')}")

# Try PATCH
print("\nTrying PATCH to enable sleep-time...")
response = requests.patch(
    f"{LETTA_URL}/v1/agents/{AGENT_ID}",
    json={"enable_sleeptime": True},
    headers={"Content-Type": "application/json"}
)
print(f"Status: {response.status_code}")

if response.status_code in [200, 201]:
    updated = response.json()
    print(f"After PATCH:")
    print(f"  Enable sleep-time: {updated.get('enable_sleeptime')}")
    print(f"  Managed group: {updated.get('managed_group')}")
    
    if updated.get('managed_group'):
        print("\n✓ Sleep-time ABILITATO con successo!")
    else:
        print("\n⚠️ PATCH ok ma managed_group non creato")
else:
    print(f"✗ Error: {response.text[:300]}")
