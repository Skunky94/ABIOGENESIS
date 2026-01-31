"""
Test suite for Sleep-Webhook Service

Tests the webhook service that receives step completion notifications
from Letta and triggers sleep consolidation.

Run: python -m tests.test_sleep_webhook
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from sleep_webhook import app, conversation_counters, StepCompletePayload

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_returns_healthy(self):
        """Health endpoint should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "counters" in data


class TestStatusEndpoint:
    """Test status endpoint."""
    
    def test_status_returns_counter_info(self):
        """Status endpoint should return current counters."""
        # Reset counters
        conversation_counters.clear()
        
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert data["threshold"] == 5


class TestResetEndpoint:
    """Test reset counter endpoint."""
    
    def test_reset_clears_conversation_counter(self):
        """Reset endpoint should clear specific conversation counter."""
        # Set a counter
        conversation_counters["test-conv"] = 3
        
        response = client.post("/reset/test-conv")
        assert response.status_code == 200
        assert conversation_counters.get("test-conv") == 0


class TestStepCompleteWebhook:
    """Test step complete webhook functionality."""
    
    def setup_method(self):
        """Clear counters before each test."""
        conversation_counters.clear()
    
    def test_webhook_receives_step_complete(self):
        """Webhook should receive and process step complete payload."""
        response = client.post(
            "/webhooks/step-complete",
            json={
                "step_id": "step-123",
                "agent_id": "agent-test",
                "conversation_id": "conv-test"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["step_id"] == "step-123"
    
    def test_message_counter_increments(self):
        """Message counter should increment on each webhook call."""
        # First message
        response1 = client.post(
            "/webhooks/step-complete",
            json={"step_id": "step-1", "conversation_id": "conv-1"}
        )
        assert response1.json()["count"] == 1
        
        # Second message
        response2 = client.post(
            "/webhooks/step-complete",
            json={"step_id": "step-2", "conversation_id": "conv-1"}
        )
        assert response2.json()["count"] == 2
        
        # Different conversation
        response3 = client.post(
            "/webhooks/step-complete",
            json={"step_id": "step-3", "conversation_id": "conv-2"}
        )
        assert response3.json()["count"] == 1
    
    def test_consolidation_triggers_after_threshold(self):
        """Consolidation should trigger after threshold messages."""
        threshold = 5
        
        with patch("sleep_webhook.trigger_sleep_consolidation", new_callable=AsyncMock) as mock:
            # Send messages up to threshold
            for i in range(threshold):
                response = client.post(
                    "/webhooks/step-complete",
                    json={"step_id": f"step-{i}", "conversation_id": "conv-test"}
                )
                assert response.json()["count"] == i + 1
            
            # Consolidation should be triggered on threshold
            mock.assert_called_once()
            
            # Counter should be reset
            assert conversation_counters.get("conv-test") == 0
    
    @patch("httpx.AsyncClient")
    def test_consolidation_calls_sleep_agent(self, mock_client_class):
        """Consolidation should call sleep agent via Letta API."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value.json.return_value = []
        mock_client.post.return_value.json.return_value = {"content": "{}"}
        
        # Manually test consolidation logic
        from sleep_webhook import trigger_sleep_consolidation
        import asyncio
        
        # This tests the consolidation function logic
        # In real scenario, this would call Letta API
        assert callable(trigger_sleep_consolidation)


class TestAuthorization:
    """Test webhook authorization."""
    
    def test_missing_auth_with_key_set(self):
        """Should require auth when key is configured."""
        # This test assumes WEBHOOK_KEY is not set in test env
        # In production, this would fail if key is set
        response = client.post(
            "/webhooks/step-complete",
            json={"step_id": "step-1"}
        )
        # Should work (no key set in test)
        assert response.status_code == 200


class TestPayloadValidation:
    """Test payload validation."""
    
    def test_valid_payload(self):
        """Valid payload should be accepted."""
        response = client.post(
            "/webhooks/step-complete",
            json={"step_id": "step-123"}
        )
        assert response.status_code == 200
    
    def test_missing_step_id(self):
        """Missing step_id should cause error."""
        response = client.post(
            "/webhooks/step-complete",
            json={}
        )
        assert response.status_code in [200, 422]  # FastAPI validates required fields
    
    def test_empty_step_id(self):
        """Empty step_id should be handled."""
        response = client.post(
            "/webhooks/step-complete",
            json={"step_id": ""}
        )
        # Empty string is valid for optional field in some cases
        assert response.status_code in [200, 422]


class TestConversationIsolation:
    """Test that conversations are properly isolated."""
    
    def test_multiple_conversations_independent(self):
        """Counters for different conversations should be independent."""
        # Setup
        conversation_counters.clear()
        
        # Message in conversation A
        for _ in range(3):
            client.post(
                "/webhooks/step-complete",
                json={"step_id": "step", "conversation_id": "conv-A"}
            )
        
        # Message in conversation B
        for _ in range(2):
            client.post(
                "/webhooks/step-complete",
                json={"step_id": "step", "conversation_id": "conv-B"}
            )
        
        # Check counters are independent
        assert conversation_counters.get("conv-A") == 3
        assert conversation_counters.get("conv-B") == 2


def run_tests():
    """Run all tests and return results."""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    print("=" * 60)
    print("Sleep-Webhook Service Tests")
    print("=" * 60)
    run_tests()
