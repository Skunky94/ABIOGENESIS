#!/usr/bin/env python3
"""
Register 'remember' Tool with Scarlet Agent

ADR-005 Phase 6: Conscious Memory Retrieval Tool Registration

This script registers the remember tool with the primary Scarlet agent,
allowing her to perform intentional memory searches.

Usage:
    python register_remember_tool.py

Author: ABIOGENESIS Team
Date: 2026-02-01
"""

import os
import sys
from letta_client import Letta

# Configuration
LETTA_URL = os.getenv("LETTA_URL", "http://localhost:8283")
PRIMARY_AGENT_ID = "agent-ac26cf86-3890-40a9-a70f-967f05115da9"

# Tool source code (calls webhook endpoint)
TOOL_SOURCE_CODE = '''
def remember(query: str, memory_types: list = None, limit: int = 5) -> str:
    """
    Cerca nella tua memoria episodica, semantica e procedurale.
    
    Usa questo strumento quando vuoi ricordare:
    - Conversazioni passate ("cosa mi ha detto Davide ieri?")
    - Fatti e conoscenze ("cosa so di ABIOGENESIS?")
    - Decisioni prese ("quali decisioni abbiamo preso sul database?")
    - Procedure apprese ("come si fa X?")
    
    Args:
        query: Query in linguaggio naturale
        memory_types: Tipi di memoria da cercare (default: tutti)
                     Opzioni: ["episodes", "concepts", "skills", "emotions"]
        limit: Numero massimo di risultati (default: 5)
        
    Returns:
        Stringa formattata con i ricordi trovati
    """
    import requests
    
    webhook_url = "http://sleep-webhook:8284"
    
    try:
        response = requests.post(
            f"{webhook_url}/tools/remember",
            json={
                "query": query,
                "memory_types": memory_types or ["episodes", "concepts", "skills", "emotions"],
                "limit": limit
            },
            timeout=30.0
        )
        response.raise_for_status()
        return response.json().get("result", "[Nessun risultato]")
    except Exception as e:
        return f"[Errore durante la ricerca nella memoria: {e}]"
'''


def main():
    print(f"[RegisterTool] Connecting to Letta at {LETTA_URL}...")
    
    try:
        client = Letta(base_url=LETTA_URL)
        
        # Verify agent exists
        print(f"[RegisterTool] Verifying agent {PRIMARY_AGENT_ID}...")
        agent = client.agents.retrieve(PRIMARY_AGENT_ID)
        print(f"[RegisterTool] Agent found: {agent.name}")
        
        # Check if tool already exists
        print("[RegisterTool] Checking existing tools...")
        existing_tools = client.tools.list()
        
        remember_tool = None
        for tool in existing_tools:
            if tool.name == "remember":
                remember_tool = tool
                print(f"[RegisterTool] Found existing 'remember' tool: {tool.id}")
                break
        
        # Create or update tool
        if remember_tool is None:
            print("[RegisterTool] Creating 'remember' tool...")
            remember_tool = client.tools.create(
                source_code=TOOL_SOURCE_CODE,
                tags=["memory", "retrieval", "adr-005"]
            )
            print(f"[RegisterTool] Created tool: {remember_tool.id} (name: {remember_tool.name})")
        else:
            print("[RegisterTool] Updating existing tool...")
            remember_tool = client.tools.update(
                tool_id=remember_tool.id,
                source_code=TOOL_SOURCE_CODE,
                tags=["memory", "retrieval", "adr-005"]
            )
            print(f"[RegisterTool] Updated tool: {remember_tool.id}")
        
        # Check if already attached to agent
        print("[RegisterTool] Checking agent tools...")
        agent_tools = client.agents.tools.list(agent_id=PRIMARY_AGENT_ID)
        
        already_attached = False
        for tool in agent_tools:
            if tool.name == "remember":
                already_attached = True
                print(f"[RegisterTool] Tool already attached to agent")
                break
        
        # Attach to agent if not already
        if not already_attached:
            print("[RegisterTool] Attaching tool to agent...")
            client.agents.tools.attach(
                agent_id=PRIMARY_AGENT_ID,
                tool_id=remember_tool.id
            )
            print(f"[RegisterTool] Tool attached successfully!")
        
        # Verify
        print("\n" + "="*60)
        print("✅ REGISTRATION COMPLETE")
        print("="*60)
        print(f"Tool Name: remember")
        print(f"Tool ID: {remember_tool.id}")
        print(f"Agent: {agent.name} ({PRIMARY_AGENT_ID})")
        print("\nScarlet può ora usare remember() per cercare nella sua memoria!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
