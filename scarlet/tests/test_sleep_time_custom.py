"""
Test Custom Sleep-Time Agent Implementation
============================================

This script tests the custom sleep-time agent functionality
that was implemented as an alternative to Letta's buggy built-in.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from scarlet.src.scarlet_agent import ScarletAgent, ScarletConfig, SleepAgentConfig


def test_sleep_time_creation():
    """Test creating agent with custom sleep-time."""
    print("\n" + "=" * 60)
    print("TEST 1: Creating Scarlet with Custom Sleep-Time Agent")
    print("=" * 60)
    
    config = ScarletConfig(
        model="minimax/MiniMax-M2.1",
        sleep_enabled=True,
        sleep_messages_threshold=3  # Test with low threshold
    )
    
    scarlet = ScarletAgent(config)
    
    try:
        agent_id = scarlet.create(with_sleep_agent=True)
        print(f"✓ Primary agent created: {agent_id}")
        
        # Check sleep agent
        if scarlet._sleep_agent and scarlet._sleep_agent.is_created:
            print(f"✓ Sleep-time agent created: {scarlet._sleep_agent._agent_id}")
        else:
            print("✗ Sleep-time agent NOT created")
            return False
        
        # Check orchestrator
        if scarlet._orchestrator:
            status = scarlet._orchestrator.get_status()
            print(f"✓ Orchestrator initialized")
            print(f"  - Threshold: {status['threshold']} messages")
            print(f"  - Auto-trigger: {status['auto_trigger']}")
        else:
            print("✗ Orchestrator NOT initialized")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_messaging():
    """Test that messaging works and triggers sleep-time."""
    print("\n" + "=" * 60)
    print("TEST 2: Testing Message Exchange with Sleep-Time")
    print("=" * 60)
    
    scarlet = ScarletAgent()
    
    if not scarlet.is_created:
        print("Creating agent first...")
        scarlet.create(with_sleep_agent=True)
    
    try:
        # Send a few messages
        print("\nSending messages to trigger sleep-time...")
        responses = []
        for i in range(4):  # Threshold is 3
            msg = f"Test message {i+1}"
            print(f"  User: {msg}")
            response = scarlet.chat(msg)
            responses.append(response)
            print(f"  Scarlet: {response[:100]}...")
        
        # Check orchestrator state
        status = scarlet.sleep_status
        print(f"\nOrchestrator state after {4} messages:")
        print(f"  - Message count: {status['message_count']}")
        print(f"  - Consolidations run: {status['consolidation_count']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_manual_consolidation():
    """Test manual consolidation trigger."""
    print("\n" + "=" * 60)
    print("TEST 3: Testing Manual Consolidation")
    print("=" * 60)
    
    scarlet = ScarletAgent()
    
    if not scarlet.is_created:
        print("Creating agent first...")
        scarlet.create(with_sleep_agent=True)
    
    try:
        print("\nTriggering manual consolidation...")
        insights = scarlet.force_consolidation()
        
        if insights:
            print("✓ Consolidation successful!")
            print(f"  - Persona updates: {len(insights.get('persona_updates', []))}")
            print(f"  - Human updates: {len(insights.get('human_updates', []))}")
            print(f"  - Goals insights: {len(insights.get('goals_insights', []))}")
            print(f"  - Reflection: {insights.get('reflection', 'N/A')[:100]}...")
            return True
        else:
            print("✗ Consolidation returned no insights")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_sleep_status():
    """Test getting sleep-time status."""
    print("\n" + "=" * 60)
    print("TEST 4: Checking Sleep-Time Status")
    print("=" * 60)
    
    scarlet = ScarletAgent()
    
    if not scarlet.is_created:
        print("Creating agent first...")
        scarlet.create(with_sleep_agent=True)
    
    try:
        status = scarlet.sleep_status
        
        print("\nSleep-Time System Status:")
        print(f"  Enabled: {scarlet.is_sleep_enabled}")
        print(f"  Sleep Agent Created: {status['sleep_agent_created']}")
        print(f"  Primary Agent Created: {status['primary_agent_created']}")
        print(f"  Message Count: {status['message_count']}")
        print(f"  Threshold: {status['threshold']}")
        print(f"  Auto-Trigger: {status['auto_trigger']}")
        print(f"  Last Consolidation: {status['last_consolidation']}")
        print(f"  Total Consolidations: {status['consolidation_count']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_agent_deletion():
    """Test that deletion cleans up both agents."""
    print("\n" + "=" * 60)
    print("TEST 5: Testing Agent Deletion")
    print("=" * 60)
    
    # Create fresh agent
    scarlet = ScarletAgent()
    scarlet.create(with_sleep_agent=True)
    
    primary_id = scarlet._agent_id
    sleep_id = scarlet._sleep_agent._agent_id if scarlet._sleep_agent else None
    
    print(f"Primary agent: {primary_id}")
    print(f"Sleep agent: {sleep_id}")
    
    try:
        print("\nDeleting agents...")
        scarlet.delete()
        
        # Verify deletion
        if not scarlet.is_created:
            print("✓ Primary agent deleted")
        else:
            print("✗ Primary agent still exists")
            return False
        
        if scarlet._sleep_agent and not scarlet._sleep_agent.is_created:
            print("✓ Sleep agent deleted")
        elif scarlet._sleep_agent is None:
            print("✓ Sleep agent reference cleared")
        else:
            print("✗ Sleep agent still exists")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Custom Sleep-Time Agent Test Suite")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key or api_key == "your_minimax_api_key_here":
        print("ERROR: MINIMAX_API_KEY not configured in .env")
        sys.exit(1)
    
    # Check Letta server
    scarlet = ScarletAgent()
    print("\nChecking Letta server...")
    if not scarlet.ping():
        print("ERROR: Cannot connect to Letta server")
        print("Make sure Docker containers are running:")
        print("  cd scarlet && docker compose up -d")
        sys.exit(1)
    print("Letta server OK")
    
    # Run tests
    tests = [
        ("Sleep-Time Creation", test_sleep_time_creation),
        ("Message Exchange", test_messaging),
        ("Manual Consolidation", test_manual_consolidation),
        ("Status Check", test_sleep_status),
        ("Agent Deletion", test_agent_deletion),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
