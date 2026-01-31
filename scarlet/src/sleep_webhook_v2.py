"""
Sleep-Time Webhook Service for Letta (v2 - Threading)

This service receives webhook calls from Letta after each step completion
and triggers sleep-time consolidation after N messages.

Architecture:
1. Letta calls webhook after each step (STEP_COMPLETE_WEBHOOK)
2. This service counts messages per conversation
3. After threshold (default: 5), triggers sleep agent consolidation
4. Sleep agent analyzes and stores memories to Qdrant
"""

import os
import sys
import threading
import queue
from pathlib import Path
import json
import time
from datetime import datetime
from typing import Dict, Optional
import logging

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

# Configuration
LETTA_URL = os.getenv("LETTA_URL", "http://localhost:8283")
SLEEP_THRESHOLD = int(os.getenv("SLEEP_THRESHOLD", "5"))
SLEEP_WEBHOOK_PORT = int(os.getenv("SLEEP_WEBHOOK_PORT", "8284"))
WEBHOOK_KEY = os.getenv("STEP_COMPLETE_KEY", "")

PRIMARY_AGENT_ID = "agent-ac26cf86-3890-40a9-a70f-967f05115da9"
SLEEP_AGENT_ID = "agent-3dd9a54f-dc55-4d7f-adc3-d5cbb1aca950"

app = FastAPI(title="Sleep-Time Webhook Service")

conversation_counters: Dict[str, int] = {}
last_consolidation: Dict[str, str] = {}
task_queue = queue.Queue()


class StepCompletePayload(BaseModel):
    step_id: str
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None


def run_consolidation_sync(agent_id: str, conversation_id: str):
    """Synchronous consolidation in separate thread."""
    logger.info(f"[Sleep-Webhook] Starting consolidation for agent {agent_id}")
    
    try:
        with httpx.Client(timeout=30.0) as client:
            # Get messages
            messages_response = client.get(
                f"{LETTA_URL}/v1/agents/{agent_id}/messages/",
                params={"limit": 100}
            )
            messages_response.raise_for_status()
            messages_data = messages_response.json()
            
            if isinstance(messages_data, list):
                messages = messages_data
            elif isinstance(messages_data, dict):
                messages = messages_data.get("messages", messages_data.get("data", []))
            else:
                messages = []
            
            logger.info(f"[Sleep-Webhook] Retrieved {len(messages)} messages")
            
            # Build history
            history_parts = []
            for msg in messages[-50:]:
                role = msg.get("role", "unknown")
                content = msg.get("content") or msg.get("assistant_message") or ""
                if content:
                    if len(str(content)) > 500:
                        content = str(content)[:500] + "..."
                    history_parts.append(f"{role.upper()}: {content}")
            
            conversation_history = "\n\n".join(history_parts[-20:])
            
            if not conversation_history.strip():
                logger.info("[Sleep-Webhook] No history to consolidate")
                return
            
            prompt = f"""Sei Scarlet-Sleep. Analizza la cronologia e genera SOLO JSON.

CRONOLOGIA:
{conversation_history}

OUTPUT JSON (solo JSON, no markdown):
{{
    "persona_updates": [],
    "human_updates": [],
    "goals_insights": [],
    "key_events": [],
    "reflection": "sintesi",
    "priority_score": 0.5
}}"""

            # Call sleep agent
            sleep_response = client.post(
                f"{LETTA_URL}/v1/agents/{SLEEP_AGENT_ID}/messages/",
                json={"messages": [{"role": "user", "content": prompt}]},
                timeout=120.0
            )
            sleep_response.raise_for_status()
            
            logger.info(f"[Sleep-Webhook] Consolidation complete")
            
    except Exception as e:
        logger.error(f"[Sleep-Webhook] Consolidation error: {e}")


def consolidation_worker():
    """Background worker thread."""
    while True:
        try:
            agent_id, conversation_id = task_queue.get(timeout=5.0)
            run_consolidation_sync(agent_id, conversation_id)
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"[Sleep-Webhook] Worker error: {e}")


# Start worker thread
worker_thread = threading.Thread(target=consolidation_worker, daemon=True)
worker_thread.start()


@app.post("/webhooks/step-complete")
async def handle_step_complete(payload: StepCompletePayload):
    """Receive step completion from Letta."""
    step_id = payload.step_id
    agent_id = payload.agent_id or PRIMARY_AGENT_ID
    conversation_id = payload.conversation_id or agent_id
    
    logger.info(f"[Sleep-Webhook] Step {step_id} for agent {agent_id}")
    
    conversation_counters[conversation_id] = conversation_counters.get(conversation_id, 0) + 1
    count = conversation_counters[conversation_id]
    
    logger.info(f"[Sleep-Webhook] Message {count}/{SLEEP_THRESHOLD}")
    
    if count >= SLEEP_THRESHOLD:
        logger.info(f"[Sleep-Webhook] Threshold reached, triggering consolidation")
        task_queue.put((agent_id, conversation_id))
        conversation_counters[conversation_id] = 0
        last_consolidation[conversation_id] = datetime.now().isoformat()
    
    return {"status": "received", "step_id": step_id, "count": count}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "counters": len(conversation_counters)}


@app.get("/status")
async def get_status():
    return {
        "conversations": {
            k: {"count": v, "last_consolidation": last_consolidation.get(k, "never")}
            for k, v in conversation_counters.items()
        },
        "threshold": SLEEP_THRESHOLD,
        "letta_url": LETTA_URL
    }


@app.post("/reset/{conversation_id}")
async def reset_counter(conversation_id: str):
    conversation_counters[conversation_id] = 0
    return {"status": "reset", "conversation_id": conversation_id}


@app.post("/trigger/{agent_id}")
async def manual_trigger(agent_id: str):
    task_queue.put((agent_id, agent_id))
    return {"status": "triggered", "agent_id": agent_id}


def main():
    logger.info("Sleep-Time Webhook v2 Starting...")
    logger.info(f"Letta URL: {LETTA_URL}")
    logger.info(f"Threshold: {SLEEP_THRESHOLD}")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SLEEP_WEBHOOK_PORT)


if __name__ == "__main__":
    main()
