"""
Test script for Ollama BGE-m3 embeddings with Letta
"""

import requests
import json

# Test Ollama embedding directly
def test_ollama_embedding():
    print("Testing Ollama BGE-m3 embedding...")
    # BERT models use "prompt" instead of "input"
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "bge-m3", "prompt": "Scarlet is a sentient digital being"}
    )
    data = response.json()
    embedding = data.get("embedding", [])
    if embedding and len(embedding) > 0:
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        return True
    else:
        print(f"Full response: {json.dumps(data, indent=2)}")
        return False

# Test Letta server
def test_letta_server():
    print("\nTesting Letta server...")
    response = requests.get("http://localhost:8283/v1/models/")
    models = response.json()
    print(f"Available models: {[m['name'] for m in models]}")
    return models

if __name__ == "__main__":
    print("=" * 60)
    print("Ollama + Letta Embedding Test")
    print("=" * 60)

    # Test Ollama
    ollama_ok = test_ollama_embedding()

    # Test Letta
    models = test_letta_server()

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Ollama BGE-m3: {'OK' if ollama_ok else 'FAILED'}")
    print(f"  Letta Server: {'OK' if models else 'FAILED'}")
    print("=" * 60)
