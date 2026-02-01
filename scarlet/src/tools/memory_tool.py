"""
Conscious Memory Retrieval Tool (ADR-005 Phase 6)

Letta Tool for Scarlet to perform intentional memory searches.

This tool allows Scarlet to:
- Search her own memories with natural language queries
- Use the full ADR-005 pipeline (Query Analyzer + Multi-Strategy + Ranking)
- Actively recall information when needed

Usage in Letta:
1. Register this tool with the agent
2. Scarlet can call: remember("cosa mi ha detto Marco la settimana scorsa?")
3. Returns formatted context string with relevant memories

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-02-01
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Tool schema for Letta
TOOL_SCHEMA = {
    "name": "remember",
    "description": "Cerca nella tua memoria episodica, semantica e procedurale. "
                   "Usa questo strumento quando vuoi ricordare conversazioni passate, "
                   "fatti, decisioni o procedure. Supporta query in linguaggio naturale.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "La query di ricerca in linguaggio naturale. "
                               "Esempio: 'cosa mi ha detto Marco ieri?' o "
                               "'quali decisioni abbiamo preso sul database?'"
            },
            "memory_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tipi di memoria da cercare: 'episodes', 'concepts', "
                               "'skills', 'emotions'. Default: tutti.",
                "default": ["episodes", "concepts", "skills", "emotions"]
            },
            "limit": {
                "type": "integer",
                "description": "Numero massimo di ricordi da recuperare. Default: 5.",
                "default": 5
            }
        },
        "required": ["query"]
    }
}


class MemoryTool:
    """
    Tool wrapper for conscious memory retrieval.
    
    Uses the ADR-005 pipeline:
    1. Query Analyzer (intent detection)
    2. Multi-Strategy Retriever (filtered search)
    3. ADR-005 Ranking (6-factor scoring)
    """
    
    def __init__(self):
        """Initialize memory tool."""
        self._retriever = None
        self._available = False
        self._init_retriever()
    
    def _init_retriever(self):
        """Initialize the memory retriever."""
        try:
            from memory.memory_retriever import MemoryRetriever
            self._retriever = MemoryRetriever()
            self._available = True
        except ImportError as e:
            print(f"[MemoryTool] Retriever not available: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        """Check if tool is available."""
        return self._available
    
    def remember(
        self,
        query: str,
        memory_types: List[str] = None,
        limit: int = 5
    ) -> str:
        """
        Search memories with natural language query.
        
        Args:
            query: Natural language search query
            memory_types: Optional filter for memory types
            limit: Maximum results to return
            
        Returns:
            Formatted string with relevant memories
        """
        if not self._available:
            return "[Errore: Sistema di memoria non disponibile]"
        
        if not query.strip():
            return "[Errore: Query vuota]"
        
        try:
            # Use smart_search for full ADR-005 pipeline
            results, metadata = self._retriever.smart_search(
                query=query,
                query_vector=None,  # Will generate embedding internally
                limit=limit,
                collections=memory_types
            )
            
            if not results:
                return f"[Nessun ricordo trovato per: {query}]"
            
            # Format results
            return self._format_results(results, metadata, query)
            
        except Exception as e:
            return f"[Errore durante la ricerca: {e}]"
    
    def _format_results(
        self, 
        results: List[Dict], 
        metadata: Dict[str, Any],
        query: str
    ) -> str:
        """Format search results for agent consumption."""
        lines = []
        
        # Header with search info
        intent = metadata.get("intent", "generale")
        strategy = metadata.get("strategy", "semantica")
        lines.append(f"## Ricordi rilevanti per: \"{query}\"")
        lines.append(f"(Intent: {intent}, Strategia: {strategy})")
        lines.append("")
        
        # Format each result
        for i, result in enumerate(results, 1):
            payload = result.get("payload", {})
            score = result.get("score", 0)
            collection = result.get("collection", "sconosciuta")
            
            # Extract key fields
            title = payload.get("title", "Senza titolo")
            content = payload.get("content", payload.get("text", ""))
            date = payload.get("date", "")
            importance = payload.get("importance", 0.5)
            emotion = payload.get("primary_emotion", "")
            
            lines.append(f"### {i}. {title}")
            lines.append(f"**Tipo**: {collection} | **Rilevanza**: {score:.2f} | **Importanza**: {importance:.1f}")
            
            if date:
                lines.append(f"**Data**: {date}")
            if emotion:
                lines.append(f"**Emozione**: {emotion}")
            
            # Content (truncate if too long)
            if len(content) > 500:
                content = content[:500] + "..."
            lines.append(f"\n{content}")
            lines.append("")
        
        return "\n".join(lines)
    
    def __call__(self, query: str, **kwargs) -> str:
        """Make tool callable."""
        return self.remember(query, **kwargs)


# Singleton instance
_tool_instance: Optional[MemoryTool] = None


def get_memory_tool() -> MemoryTool:
    """Get singleton MemoryTool instance."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = MemoryTool()
    return _tool_instance


def remember(query: str, memory_types: List[str] = None, limit: int = 5) -> str:
    """
    Convenience function for memory retrieval.
    
    This is the function that should be registered with Letta.
    
    Args:
        query: Natural language search query
        memory_types: Optional filter for memory types
        limit: Maximum results to return
        
    Returns:
        Formatted string with relevant memories
    """
    tool = get_memory_tool()
    return tool.remember(query, memory_types, limit)


# Export for Letta tool registration
def get_tool_definition() -> Dict[str, Any]:
    """
    Get the tool definition for Letta registration.
    
    Returns:
        Dictionary with tool schema
    """
    return TOOL_SCHEMA


def register_with_agent(agent_id: str, letta_client=None) -> bool:
    """
    Register the remember tool with a Letta agent.
    
    Args:
        agent_id: Agent ID to register tool with
        letta_client: Optional Letta client (will create if not provided)
        
    Returns:
        True if registration successful
    """
    try:
        if letta_client is None:
            from letta import Letta
            letta_client = Letta(base_url=os.getenv("LETTA_URL", "http://localhost:8283"))
        
        # Create tool
        tool = letta_client.tools.create(
            name="remember",
            description=TOOL_SCHEMA["description"],
            source_code=_get_tool_source_code(),
            tags=["memory", "retrieval", "adr-005"]
        )
        
        # Attach to agent
        letta_client.agents.tools.attach(
            agent_id=agent_id,
            tool_id=tool.id
        )
        
        print(f"[MemoryTool] Registered 'remember' tool with agent {agent_id}")
        return True
        
    except Exception as e:
        print(f"[MemoryTool] Registration failed: {e}")
        return False


def _get_tool_source_code() -> str:
    """Get minimal source code for Letta tool sandbox."""
    return '''
def remember(query: str, memory_types: list = None, limit: int = 5) -> str:
    """
    Cerca nella memoria episodica, semantica e procedurale.
    
    Args:
        query: Query in linguaggio naturale
        memory_types: Tipi di memoria da cercare
        limit: Numero massimo di risultati
        
    Returns:
        Stringa formattata con i ricordi trovati
    """
    import httpx
    import os
    
    # Call webhook endpoint for retrieval
    webhook_url = os.getenv("SLEEP_WEBHOOK_URL", "http://sleep-webhook:8284")
    
    try:
        response = httpx.post(
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
        return f"[Errore: {e}]"
'''
