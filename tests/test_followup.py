"""Test multi-turn follow-up and client persistence in AIService."""
import os
import sys
import gc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ai_service import AIService
from src.config import Config


def test_client_persistence():
    print("Testing AIService client persistence...")
    ai = AIService()
    client = ai._get_client()
    assert client is not None
    assert ai._client is not None

    # Simulate garbage collection
    gc.collect()

    # Verify client is still open
    httpx_client = getattr(ai._client._api_client, "_httpx_client", None)
    assert httpx_client is not None
    assert not httpx_client.is_closed, "Client should remain open after GC"
    print("[OK] Persistent client remains open across GC cycles")


if __name__ == "__main__":
    if Config.is_configured():
        test_client_persistence()
        print("=== Follow-up Client Tests Passed ===")
    else:
        print("Skipping live test: API key not configured in test environment")
