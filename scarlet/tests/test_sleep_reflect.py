"""
Real Sleep-Time Test: 5 turns of reflection

Turn 1: "Ragiona sugli ultimi test"
Turn 2-5: "rifletti" (4 volte)

After 5 messages, sleep-time should trigger automatically.

Author: ABIOGENESIS Team
Date: 2026-02-01
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def test_sleep_reflection_5_turns():
    """Test sleep-time trigger after 5 reflection turns."""
    logger.info("=" * 70)
    logger.info("SLEEP-TIME REFLECTION TEST - 5 TURNS")
    logger.info("=" * 70)
    
    try:
        from scarlet_agent import ScarletAgent, ScarletConfig
        
        # Configuration
        config = ScarletConfig(
            name="Scarlet-Test",
            model="minimax/MiniMax-M2.1",
            sleep_messages_threshold=5,  # Trigger after 5 messages
            sleep_enabled=True
        )
        
        # Create agent
        logger.info("\n[1] Creating Scarlet agent...")
        scarlet = ScarletAgent(config)
        agent_id = scarlet.create(with_sleep_agent=True)
        logger.info(f"    Agent ID: {agent_id}")
        
        # Show initial status
        status = scarlet.sleep_status
        logger.info(f"    Initial message_count: {status['message_count']}")
        logger.info(f"    Threshold: {status['threshold']}")
        
        # Test messages
        messages = [
            "Ragiona sugli ultimi test che hai eseguito e sul tuo stato attuale.",
            "rifletti",
            "rifletti",
            "rifletti",
            "rifletti"
        ]
        
        # Send messages
        for i, msg in enumerate(messages, 1):
            logger.info(f"\n[2.{i}] Sending: '{msg}'")
            response = scarlet.chat(msg)
            
            # Show response summary
            response_preview = response[:200] + "..." if len(response) > 200 else response
            logger.info(f"    Response: {response_preview}")
            
            # Check sleep status after each message
            status = scarlet.sleep_status
            logger.info(f"    Message count: {status['message_count']}/{status['threshold']}")
            
            if status['message_count'] >= status['threshold']:
                logger.info(f"\n    ⚡ SLEEP-TIME TRIGGERED!")
                logger.info(f"    Last consolidation: {status['last_consolidation']}")
        
        # Final status
        logger.info("\n" + "=" * 70)
        logger.info("FINAL STATUS")
        logger.info("=" * 70)
        
        status = scarlet.sleep_status
        logger.info(f"    Message count: {status['message_count']}")
        logger.info(f"    Threshold reached: {status['message_count'] >= status['threshold']}")
        logger.info(f"    Last consolidation: {status['last_consolidation']}")
        logger.info(f"    Consolidation history: {len(status['consolidation_history'])} runs")
        
        # Check if consolidation happened
        if status['consolidation_count'] > 0:
            logger.info("\n✅ SLEEP-TIME WORKED!")
            logger.info(f"    Consolidations performed: {status['consolidation_count']}")
        else:
            logger.info("\n⚠️ Sleep-time may not have triggered (check Letta server)")
        
        # Show memory stats if available
        if scarlet.memory_manager:
            stats = scarlet.memory_manager.get_memory_stats()
            logger.info(f"\nMemory Stats:")
            logger.info(f"    Total memories: {stats.get('total_memories', 'N/A')}")
            logger.info(f"    Qdrant status: {stats.get('qdrant_connected', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sleep_reflection_5_turns()
    sys.exit(0 if success else 1)
