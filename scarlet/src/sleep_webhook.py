"""
Sleep-Time Webhook Service for Letta

This service receives webhook calls from Letta after each step completion
and triggers sleep-time consolidation after N messages.

Architecture:
1. Letta calls webhook after each step (STEP_COMPLETE_WEBHOOK)
2. This service counts messages per conversation
3. After threshold (default: 5), triggers sleep agent consolidation
4. Sleep agent analyzes conversation and returns JSON insights
5. Insights are stored in Qdrant (episodic, semantic, procedural, emotional)

Environment Variables:
- LETTA_URL: Letta server URL (default: http://localhost:8283)
- SLEEP_THRESHOLD: Messages before consolidation (default: 5)
- SLEEP_WEBHOOK_PORT: Port for this service (default: 8284)
- STEP_COMPLETE_KEY: Optional auth key for webhook

Usage:
1. Start this service: python sleep_webhook.py
2. Configure Letta: STEP_COMPLETE_WEBHOOK=http://localhost:8284/webhooks/step-complete
3. Messages are automatically counted
4. Sleep consolidation triggers automatically with Qdrant storage
"""

import os
import sys
from pathlib import Path
import json
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import logging

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import httpx

# Import memory system for Qdrant storage
try:
    from memory.memory_blocks import MemoryManager
    from memory.qdrant_manager import get_manager
    MEMORY_AVAILABLE = True
    logger.info("[Sleep-Webhook] Memory system available")
except ImportError as e:
    logger.warning(f"[Sleep-Webhook] Memory system not available: {e}")
    MEMORY_AVAILABLE = False

# Configuration
LETTA_URL = os.getenv("LETTA_URL", "http://localhost:8283")
SLEEP_THRESHOLD = int(os.getenv("SLEEP_THRESHOLD", "5"))
SLEEP_WEBHOOK_PORT = int(os.getenv("SLEEP_WEBHOOK_PORT", "8284"))
WEBHOOK_KEY = os.getenv("STEP_COMPLETE_KEY", "")

# Official Agent IDs
PRIMARY_AGENT_ID = "agent-ac26cf86-3890-40a9-a70f-967f05115da9"
SLEEP_AGENT_ID = "agent-3dd9a54f-dc55-4d7f-adc3-d5cbb1aca950"

app = FastAPI(title="Sleep-Time Webhook Service")

# In-memory message counter per conversation
conversation_counters: Dict[str, int] = {}
last_consolidation: Dict[str, str] = {}

class StepCompletePayload(BaseModel):
    step_id: str
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None


# Initialize memory manager (singleton) - set at module level
_memory_manager: Optional[Any] = None  # Type is Any when MemoryManager not available

def get_memory_manager() -> Optional[Any]:
    """Get or initialize memory manager."""
    global _memory_manager
    if not MEMORY_AVAILABLE:
        return None
    if _memory_manager is None:
        try:
            # Import again here to avoid NameError
            from memory.memory_blocks import MemoryManager
            _memory_manager = MemoryManager()
            if _memory_manager.connect_qdrant():
                logger.info("[Sleep-Webhook] MemoryManager connected to Qdrant")
            else:
                logger.warning("[Sleep-Webhook] MemoryManager could not connect to Qdrant")
        except Exception as e:
            logger.error(f"[Sleep-Webhook] Failed to initialize MemoryManager: {e}")
            return None
    return _memory_manager


def parse_sleep_agent_response(response_text: str) -> Dict[str, Any]:
    """Parse JSON response from sleep agent."""
    try:
        # Remove markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        if text.startswith("```json"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        
        # Find JSON object
        start = text.find("{")
        end = text.rfind("}")
        
        if start != -1 and end != -1:
            json_text = text[start:end+1]
            return json.loads(json_text)
        return {}
    except json.JSONDecodeError as e:
        logger.warning(f"[Sleep-Webhook] Failed to parse JSON: {e}")
        return {}


def store_insights_to_qdrant(
    conversation_history: str, 
    insights: Dict[str, Any],
    mem_manager: MemoryManager
) -> Dict[str, int]:
    """
    Store sleep-time insights into Qdrant memory collections.
    
    Returns dict with counts of stored memories per type.
    """
    stored = {"episodic": 0, "semantic": 0, "procedural": 0, "emotional": 0}
    
    try:
        # 1. Store episodic memory from key events
        key_events = insights.get("key_events", [])
        if key_events:
            for event in key_events[:3]:  # Max 3 events
                if isinstance(event, dict) and event.get("description"):
                    mem_manager.create_episodic_memory(
                        title=f"Sleep consolidation: {event['description'][:50]}",
                        content=event["description"],
                        event_type="sleep_consolidation",
                        importance=event.get("importance", 0.5),
                        tags=["sleep_consolidation", "auto_generated"]
                    )
                    stored["episodic"] += 1
                    logger.info(f"[Sleep-Webhook] Stored episodic: {event['description'][:40]}...")
        
        # If no key events, store conversation summary
        if stored["episodic"] == 0 and conversation_history:
            reflection = insights.get("reflection", "Sleep-time consolidation")
            mem_manager.create_episodic_memory(
                title="Sleep consolidation session",
                content=reflection if reflection else conversation_history[:500],
                event_type="sleep_consolidation",
                importance=insights.get("priority_score", 0.5),
                tags=["sleep_consolidation", "auto_generated"]
            )
            stored["episodic"] = 1
        
        # 2. Store semantic memories from human_updates (facts about human)
        human_updates = insights.get("human_updates", [])
        for update in human_updates[:3]:
            if update and isinstance(update, str) and len(update) > 10:
                mem_manager.create_semantic_memory(
                    title=f"Human info: {update[:30]}",
                    content=update,
                    concept_category="human_fact",
                    confidence=0.8,
                    source="sleep_consolidation",
                    importance=0.7,
                    tags=["human", "sleep_consolidation"]
                )
                stored["semantic"] += 1
                logger.info(f"[Sleep-Webhook] Stored semantic: {update[:40]}...")
        
        # 3. Store persona updates as semantic (knowledge about self)
        persona_updates = insights.get("persona_updates", [])
        for update in persona_updates[:2]:
            if update and isinstance(update, str) and len(update) > 10:
                mem_manager.create_semantic_memory(
                    title=f"Self-knowledge: {update[:30]}",
                    content=update,
                    concept_category="self_knowledge",
                    confidence=0.75,
                    source="sleep_consolidation",
                    importance=0.6,
                    tags=["persona", "self", "sleep_consolidation"]
                )
                stored["semantic"] += 1
        
        # 4. Store goals insights as procedural (what to work on)
        goals_insights = insights.get("goals_insights", [])
        for goal in goals_insights[:2]:
            if goal and isinstance(goal, str) and len(goal) > 10:
                mem_manager.create_procedural_memory(
                    skill_name=f"Goal: {goal[:30]}",
                    content=goal,
                    procedure_type="goal_tracking",
                    importance=0.7,
                    tags=["goal", "sleep_consolidation"]
                )
                stored["procedural"] += 1
                logger.info(f"[Sleep-Webhook] Stored procedural: {goal[:40]}...")
        
        # 5. Store emotional patterns
        reflection = insights.get("reflection", "")
        if reflection and len(reflection) > 20:
            # Detect basic emotion from reflection
            emotion = "neutral"
            if any(w in reflection.lower() for w in ["curioso", "interessato", "curious"]):
                emotion = "curiosity"
            elif any(w in reflection.lower() for w in ["positivo", "soddisfatto", "bene"]):
                emotion = "satisfaction"
            elif any(w in reflection.lower() for w in ["difficile", "problema", "frustrato"]):
                emotion = "challenge"
            
            mem_manager.create_emotional_memory(
                trigger="sleep_consolidation",
                content=reflection,
                response_type=emotion,
                intensity=insights.get("priority_score", 0.5),
                context_pattern="post_conversation_reflection",
                importance=0.5,
            )
            stored["emotional"] = 1
            logger.info(f"[Sleep-Webhook] Stored emotional: {emotion}")
        
        logger.info(f"[Sleep-Webhook] Total stored: {stored}")
        return stored
        
    except Exception as e:
        logger.error(f"[Sleep-Webhook] Error storing insights: {e}")
        return stored


async def trigger_sleep_consolidation(agent_id: str, conversation_id: str):
    """Trigger sleep agent consolidation and store insights in Qdrant."""
    logger.info(f"[Sleep-Webhook] Triggering consolidation for agent {agent_id}")
    
    try:
        # Get conversation history from Letta
        # NOTE: Use follow_redirects=True to handle 307 redirects from Letta
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Get messages (NO trailing slash - causes 307 redirect!)
            messages_response = await client.get(
                f"{LETTA_URL}/v1/agents/{agent_id}/messages",
                params={"limit": 100},
                timeout=30.0
            )
            messages_response.raise_for_status()
            messages = messages_response.json()
            
            if isinstance(messages, list):
                # Build conversation history
                history_parts = []
                for msg in messages[-50:]:  # Last 50 messages
                    role = msg.get("role", "unknown")
                    content = msg.get("content", msg.get("assistant_message", ""))
                    if content:
                        history_parts.append(f"{role.upper()}: {content}")
                conversation_history = "\n\n".join(history_parts[-20:])  # Last 20 turns
            else:
                conversation_history = str(messages)
            
            if not conversation_history.strip():
                logger.info("[Sleep-Webhook] No conversation history to consolidate")
                return
            
            # Build consolidation prompt
            prompt = f"""Sei Scarlet-Sleep, un agente specializzato per il consolidamento della memoria.

ANALISI: Analizza la cronologia e genera insights JSON strutturati.

CRONOLOGIA:
{conversation_history}

OUTPUT JSON:
{{
    "persona_updates": ["insight su Scarlet"],
    "human_updates": ["info sull umano"],
    "goals_insights": ["progressi verso obiettivi"],
    "key_events": [{{"description": "evento significativo", "importance": 0.8}}],
    "reflection": "sintesi dei pattern emersi",
    "priority_score": 0.7
}}

REGOLE: Non inventare info. Solo JSON, no markdown. Sii specifico e conciso."""

            # Call sleep agent (NO trailing slash!)
            sleep_response = await client.post(
                f"{LETTA_URL}/v1/agents/{SLEEP_AGENT_ID}/messages",
                json={"messages": [{"role": "user", "content": prompt}]},
                timeout=120.0
            )
            sleep_response.raise_for_status()
            
            logger.info(f"[Sleep-Webhook] Sleep agent responded for agent {agent_id}")
            
            # Parse sleep agent response
            response_data = sleep_response.json()
            assistant_message = ""
            
            # Debug: log response structure
            logger.info(f"[Sleep-Webhook] Response type: {type(response_data)}")
            if isinstance(response_data, dict):
                logger.info(f"[Sleep-Webhook] Response keys: {list(response_data.keys())}")
                if "messages" in response_data:
                    for i, msg in enumerate(response_data["messages"][:5]):
                        if isinstance(msg, dict):
                            logger.info(f"[Sleep-Webhook] Message[{i}] type: {msg.get('message_type')} keys: {list(msg.keys())}")
            
            # Extract assistant message from response - try multiple formats
            if isinstance(response_data, dict) and "messages" in response_data:
                for msg in response_data["messages"]:
                    if isinstance(msg, dict):
                        msg_type = msg.get("message_type", "")
                        logger.debug(f"[Sleep-Webhook] Message type: {msg_type}")
                        if msg_type == "assistant_message":
                            # Try both 'content' and 'assistant_message' fields
                            assistant_message = msg.get("content", "") or msg.get("assistant_message", "")
                            if assistant_message:
                                logger.info(f"[Sleep-Webhook] Found assistant message ({len(assistant_message)} chars)")
                                break
                        # Also check for internal_monologue which may contain the response
                        elif msg_type == "internal_monologue":
                            monologue = msg.get("internal_monologue", "") or msg.get("content", "")
                            if "{" in monologue and "}" in monologue:
                                assistant_message = monologue
                                logger.info("[Sleep-Webhook] Found JSON in internal_monologue")
                                break
            elif isinstance(response_data, list):
                for msg in response_data:
                    if isinstance(msg, dict):
                        msg_type = msg.get("message_type", "")
                        if msg_type == "assistant_message":
                            assistant_message = msg.get("content", "") or msg.get("assistant_message", "")
                            break
                        elif msg_type == "internal_monologue":
                            monologue = msg.get("internal_monologue", "") or msg.get("content", "")
                            if "{" in monologue and "}" in monologue:
                                assistant_message = monologue
                                break
            
            if assistant_message:
                logger.info(f"[Sleep-Webhook] Parsing insights from response ({len(assistant_message)} chars)")
                
                # Parse JSON insights
                insights = parse_sleep_agent_response(assistant_message)
                
                if insights:
                    # Store insights in Qdrant
                    mem_manager = get_memory_manager()
                    if mem_manager:
                        stored = store_insights_to_qdrant(conversation_history, insights, mem_manager)
                        logger.info(f"[Sleep-Webhook] Stored to Qdrant: {stored}")
                    else:
                        logger.warning("[Sleep-Webhook] MemoryManager not available, skipping Qdrant storage")
                else:
                    logger.warning("[Sleep-Webhook] Could not parse insights JSON")
            else:
                logger.warning("[Sleep-Webhook] No assistant message in response")
            
            logger.info(f"[Sleep-Webhook] Consolidation complete for agent {agent_id}")
            
    except Exception as e:
        logger.error(f"[Sleep-Webhook] Error during consolidation: {e}")
            
    except Exception as e:
        logger.error(f"[Sleep-Webhook] Error during consolidation: {e}")

@app.post("/webhooks/step-complete")
async def handle_step_complete(
    payload: StepCompletePayload,
    authorization: str = Header(None)
):
    """
    Receive step completion webhook from Letta.
    Counts messages and triggers sleep consolidation when threshold reached.
    """
    # Validate authorization if key is set
    if WEBHOOK_KEY:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")
        token = authorization.replace("Bearer ", "")
        if token != WEBHOOK_KEY:
            raise HTTPException(status_code=401, detail="Invalid authorization")
    
    step_id = payload.step_id
    agent_id = payload.agent_id or PRIMARY_AGENT_ID  # Default to primary agent
    conversation_id = payload.conversation_id or agent_id  # Use agent_id as conversation identifier
    
    logger.info(f"[Sleep-Webhook] Step {step_id} completed for agent {agent_id}")
    
    # Count this message
    conversation_counters[conversation_id] = conversation_counters.get(conversation_id, 0) + 1
    count = conversation_counters[conversation_id]
    
    logger.info(f"[Sleep-Webhook] Message {count}/{SLEEP_THRESHOLD} for conversation {conversation_id}")
    
    # Check if we should trigger consolidation
    if count >= SLEEP_THRESHOLD:
        logger.info(f"[Sleep-Webhook] Threshold reached ({count}), triggering consolidation")
        
        # Trigger consolidation asynchronously
        asyncio.create_task(trigger_sleep_consolidation(agent_id, conversation_id))
        
        # Reset counter
        conversation_counters[conversation_id] = 0
        last_consolidation[conversation_id] = datetime.now().isoformat()
    
    return {"status": "received", "step_id": step_id, "count": count}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "counters": len(conversation_counters)}

@app.get("/status")
async def get_status():
    """Get current status of all conversations."""
    return {
        "conversations": {
            k: {
                "count": v,
                "last_consolidation": last_consolidation.get(k, "never")
            }
            for k, v in conversation_counters.items()
        },
        "threshold": SLEEP_THRESHOLD,
        "letta_url": LETTA_URL
    }

@app.post("/reset/{conversation_id}")
async def reset_counter(conversation_id: str):
    """Reset message counter for a conversation."""
    conversation_counters[conversation_id] = 0
    return {"status": "reset", "conversation_id": conversation_id}

def main():
    """Run the webhook service."""
    logger.info("=" * 60)
    logger.info("Sleep-Time Webhook Service Starting...")
    logger.info("=" * 60)
    logger.info(f"Letta URL: {LETTA_URL}")
    logger.info(f"Sleep Threshold: {SLEEP_THRESHOLD} messages")
    logger.info(f"Webhook Port: {SLEEP_WEBHOOK_PORT}")
    logger.info(f"Primary Agent: {PRIMARY_AGENT_ID}")
    logger.info(f"Sleep Agent: {SLEEP_AGENT_ID}")
    logger.info("=" * 60)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SLEEP_WEBHOOK_PORT)

if __name__ == "__main__":
    main()
