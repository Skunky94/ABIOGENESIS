"""
PROC-003 + PROC-006: Recreate Scarlet Agents + Register Tool

This script:
1. Creates Primary Scarlet agent
2. Creates Sleep Scarlet agent  
3. Registers 'remember' tool (ADR-005)

Usage:
    python recreate_agents_with_tool.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from letta_client import Letta

# =============================================================================
# CONFIGURATION
# =============================================================================

LETTA_URL = "http://localhost:8283"
MODEL = "minimax/MiniMax-M2.1"

PRIMARY_NAME = "Scarlet"
SLEEP_NAME = "Scarlet-Sleep"

PROMPT_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT_FILE = PROMPT_DIR / "system.txt"
SLEEP_PROMPT_FILE = PROMPT_DIR / "system_sleep.txt"

# Webhook URL for remember tool
WEBHOOK_URL = "http://sleep-webhook:8284"


# =============================================================================
# STEP 1: Connect and Verify Clean State
# =============================================================================

def connect_and_verify():
    """Connect to Letta and verify no existing agents."""
    print("\n" + "="*60)
    print("STEP 1: Connecting to Letta")
    print("="*60)
    
    client = Letta(base_url=LETTA_URL)
    
    # Check health - use correct API
    import requests
    health_resp = requests.get(f"{LETTA_URL}/v1/health")
    health_resp.raise_for_status()
    health_data = health_resp.json()
    print(f"✓ Letta healthy: v{health_data.get('version', 'unknown')}")
    
    # Check existing agents
    agents = list(client.agents.list())
    if agents:
        print(f"\n⚠️  Found {len(agents)} existing agents:")
        for a in agents:
            print(f"   - {a.name} ({a.id})")
        
        response = input("\nDelete existing agents and continue? [yes/no]: ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(1)
        
        for a in agents:
            client.agents.delete(a.id)
            print(f"   Deleted: {a.name}")
    
    print("✓ Clean state verified")
    return client


# =============================================================================
# STEP 2: Create Primary Agent
# =============================================================================

def create_primary_agent(client) -> str:
    """Create the primary Scarlet agent."""
    print("\n" + "="*60)
    print("STEP 2: Creating Primary Agent")
    print("="*60)
    
    # Load system prompt
    if not SYSTEM_PROMPT_FILE.exists():
        raise FileNotFoundError(f"System prompt not found: {SYSTEM_PROMPT_FILE}")
    
    with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    print(f"✓ Loaded system prompt ({len(system_prompt)} chars)")
    
    # Create agent
    agent = client.agents.create(
        name=PRIMARY_NAME,
        system=system_prompt,
        model=MODEL,
        context_window_limit=200000,  # MiniMax M2.1 supports 200K
        include_base_tools=True  # Include conversation_search, memory_insert, etc.
    )
    
    print(f"✓ Created {PRIMARY_NAME}: {agent.id}")
    
    # Verify configuration
    retrieved = client.agents.retrieve(agent.id)
    print(f"   Model: {retrieved.model}")
    # context_window_limit may not be exposed in AgentState, skip printing
    
    return agent.id


# =============================================================================
# STEP 3: Create Sleep Agent
# =============================================================================

def create_sleep_agent(client) -> str:
    """Create the sleep consolidation agent."""
    print("\n" + "="*60)
    print("STEP 3: Creating Sleep Agent")
    print("="*60)
    
    # Load sleep system prompt
    if not SLEEP_PROMPT_FILE.exists():
        raise FileNotFoundError(f"Sleep prompt not found: {SLEEP_PROMPT_FILE}")
    
    with open(SLEEP_PROMPT_FILE, 'r', encoding='utf-8') as f:
        sleep_prompt = f.read()
    
    print(f"✓ Loaded sleep prompt ({len(sleep_prompt)} chars)")
    
    # Create agent
    agent = client.agents.create(
        name=SLEEP_NAME,
        system=sleep_prompt,
        model=MODEL
    )
    
    print(f"✓ Created {SLEEP_NAME}: {agent.id}")
    
    return agent.id


# =============================================================================
# STEP 4: Register Remember Tool (PROC-006)
# =============================================================================

def register_remember_tool(client, agent_id: str) -> str:
    """Register the 'remember' tool with the primary agent."""
    print("\n" + "="*60)
    print("STEP 4: Registering 'remember' Tool (ADR-005)")
    print("="*60)
    
    # Check if tool already exists
    TOOL_NAME = "remember"
    all_tools = list(client.tools.list())
    existing_tool = None
    
    for tool in all_tools:
        if tool.name == TOOL_NAME:
            existing_tool = tool
            print(f"✓ Tool '{TOOL_NAME}' already exists: {tool.id}")
            break
    
    # Create tool if not exists
    if existing_tool is None:
        # CRITICAL: Name comes from function name, NOT from parameter!
        TOOL_SOURCE_CODE = f'''
def remember(query: str, limit: int = 5) -> str:
    """
    Cerca nella tua memoria a lungo termine per ricordare informazioni rilevanti.
    Usa questo tool quando hai bisogno di ricordare qualcosa che hai imparato,
    esperienze passate, conoscenze acquisite, o informazioni su persone.
    
    Args:
        query: Cosa vuoi ricordare? Descrivi in linguaggio naturale.
        limit: Numero massimo di memorie da recuperare (default: 5)
        
    Returns:
        Memorie rilevanti trovate nella tua memoria a lungo termine,
        ordinate per rilevanza secondo la formula ADR-005.
    """
    import requests
    import json
    
    WEBHOOK_URL = "{WEBHOOK_URL}"
    
    try:
        response = requests.post(
            f"{{WEBHOOK_URL}}/tools/remember",
            json={{"query": query, "limit": limit}},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        memories = data.get("memories", [])
        
        if not memories:
            return "Non ho trovato memorie rilevanti per questa ricerca."
        
        # Format memories for Scarlet
        result_parts = [f"Ho trovato {{len(memories)}} memorie rilevanti:"]
        
        for i, mem in enumerate(memories, 1):
            title = mem.get("title", "Senza titolo")
            content = mem.get("content", "")[:500]
            score = mem.get("final_score", 0)
            collection = mem.get("collection", "unknown")
            
            result_parts.append(f"\\n{{i}}. [{{collection}}] {{title}} (score: {{score:.2f}})")
            result_parts.append(f"   {{content}}")
        
        return "\\n".join(result_parts)
        
    except requests.exceptions.Timeout:
        return "Errore: timeout nella ricerca memoria. Riprova."
    except requests.exceptions.RequestException as e:
        return f"Errore nella ricerca memoria: {{str(e)}}"
    except Exception as e:
        return f"Errore imprevisto: {{str(e)}}"
'''
        
        tool = client.tools.create(
            source_code=TOOL_SOURCE_CODE
        )
        existing_tool = tool
        print(f"✓ Created tool '{TOOL_NAME}': {tool.id}")
    
    # Check if already attached
    agent_tools = list(client.agents.tools.list(agent_id=agent_id))
    tool_names = [t.name for t in agent_tools]
    
    if TOOL_NAME in tool_names:
        print(f"✓ Tool '{TOOL_NAME}' already attached to agent")
    else:
        # Attach tool to agent
        client.agents.tools.attach(
            agent_id=agent_id,
            tool_id=existing_tool.id
        )
        print(f"✓ Attached '{TOOL_NAME}' to agent")
    
    # Verify final tool list
    final_tools = list(client.agents.tools.list(agent_id=agent_id))
    print(f"\n   Agent tools ({len(final_tools)}):")
    for t in final_tools:
        print(f"   - {t.name} ({t.id})")
    
    return existing_tool.id


# =============================================================================
# STEP 5: Verify Everything
# =============================================================================

def verify_setup(client, primary_id: str, sleep_id: str, tool_id: str):
    """Final verification of the setup."""
    print("\n" + "="*60)
    print("STEP 5: Final Verification")
    print("="*60)
    
    # Verify primary agent
    primary = client.agents.retrieve(primary_id)
    print(f"✓ Primary Agent: {primary.name}")
    print(f"   ID: {primary.id}")
    print(f"   Model: {primary.model}")
    print(f"   Context: {primary.context_window_limit}")
    
    # Verify sleep agent
    sleep = client.agents.retrieve(sleep_id)
    print(f"\n✓ Sleep Agent: {sleep.name}")
    print(f"   ID: {sleep.id}")
    print(f"   Model: {sleep.model}")
    
    # Verify tool
    tool = client.tools.retrieve(tool_id)
    print(f"\n✓ Remember Tool: {tool.name}")
    print(f"   ID: {tool.id}")
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE")
    print("="*60)
    
    return {
        "primary_agent_id": primary_id,
        "sleep_agent_id": sleep_id,
        "remember_tool_id": tool_id,
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Execute full recreation procedure."""
    print("\n" + "#"*60)
    print("# PROC-003 + PROC-006: Recreate Agents + Register Tool")
    print("#"*60)
    
    try:
        # Step 1: Connect
        client = connect_and_verify()
        
        # Step 2: Create Primary
        primary_id = create_primary_agent(client)
        
        # Step 3: Create Sleep
        sleep_id = create_sleep_agent(client)
        
        # Step 4: Register Tool
        tool_id = register_remember_tool(client, primary_id)
        
        # Step 5: Verify
        result = verify_setup(client, primary_id, sleep_id, tool_id)
        
        # Print IDs for CONTEXT.md update
        print("\n" + "-"*60)
        print("UPDATE CONTEXT.md with these IDs:")
        print("-"*60)
        print(f"Primary:    {result['primary_agent_id']}")
        print(f"Sleep:      {result['sleep_agent_id']}")
        print(f"Tool:       {result['remember_tool_id']}")
        print("-"*60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
