"""
Test latency and quality of qwen2.5:1.5b for Query Analyzer
ADR-005 Phase 1 - Step 1.2
"""
import httpx
import json
import time
from datetime import datetime, timedelta

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5:1.5b"  # Best balance of speed/quality

# Test queries with expected intents
TEST_QUERIES = [
    ("Cosa abbiamo fatto ieri?", "temporal"),
    ("Cosa sai di Davide?", "entity"),
    ("Cosa ti è piaciuto della nostra conversazione?", "emotional"),
    ("Parlami di ABIOGENESIS", "topic"),
    ("Come si fa a cercare nella memoria?", "procedural"),
    ("Ciao, come stai?", "general"),
    ("Cosa abbiamo fatto la settimana scorsa con Marco?", "temporal"),
]

SYSTEM_PROMPT = """Sei un analizzatore di query per un sistema di memoria AI.
Analizza la richiesta utente e rispondi SOLO con un JSON valido (niente altro testo).

Data odierna: {today}

Il JSON deve avere questa struttura esatta:
{{
    "intent": "temporal|entity|emotional|topic|procedural|general",
    "time_reference": "string descrittivo o null",
    "resolved_date": "YYYY-MM-DD o null",
    "entities": ["lista di persone/cose menzionate"],
    "topics": ["lista argomenti"],
    "emotion_filter": "positive|negative|neutral|null"
}}

Regole:
- "ieri" = giorno precedente a oggi
- "oggi" = data odierna
- "settimana scorsa" = ultimi 7 giorni
- Se menziona una persona (Davide, Marco, etc.) -> aggiungi a entities
- Se chiede "cosa sai di" -> intent = entity
- Se chiede "come fare/si fa" -> intent = procedural
- Se chiede "ti è piaciuto/emozioni" -> intent = emotional
- Se menziona date/tempo -> intent = temporal
- Altrimenti -> intent = general"""


def test_query(query: str) -> dict:
    """Test a single query and return results with timing."""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    prompt = f"""{SYSTEM_PROMPT.format(today=today)}

Query utente: "{query}"

JSON:"""
    
    start = time.time()
    
    response = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low for consistent JSON
                "num_predict": 200   # Limit output length
            }
        },
        timeout=30.0
    )
    
    elapsed_ms = (time.time() - start) * 1000
    
    result = response.json()
    raw_response = result.get("response", "")
    
    # Try to parse JSON from response
    parsed = None
    try:
        # Clean up response - find JSON object
        json_start = raw_response.find("{")
        json_end = raw_response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = raw_response[json_start:json_end]
            parsed = json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    return {
        "query": query,
        "latency_ms": round(elapsed_ms, 1),
        "raw_response": raw_response[:500],  # Truncate
        "parsed": parsed,
        "success": parsed is not None
    }


def main():
    print("=" * 60)
    print("Query Analyzer Latency Test - qwen2.5:1.5b")
    print("=" * 60)
    print()
    
    # First, warm up the model
    print("Warming up model...")
    warmup = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": MODEL, "prompt": "Hello", "stream": False},
        timeout=60.0
    )
    print("Model ready!\n")
    
    results = []
    total_correct = 0
    total_latency = 0
    
    for query, expected_intent in TEST_QUERIES:
        print(f"Testing: '{query}'")
        result = test_query(query)
        results.append(result)
        
        latency = result["latency_ms"]
        total_latency += latency
        
        if result["success"]:
            parsed = result["parsed"]
            actual_intent = parsed.get("intent", "unknown")
            correct = actual_intent == expected_intent
            if correct:
                total_correct += 1
            
            print(f"  ✓ Latency: {latency}ms")
            print(f"  Intent: {actual_intent} (expected: {expected_intent}) {'✓' if correct else '✗'}")
            print(f"  Entities: {parsed.get('entities', [])}")
            print(f"  Time ref: {parsed.get('time_reference')}")
        else:
            print(f"  ✗ Failed to parse JSON")
            print(f"  Raw: {result['raw_response'][:100]}...")
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    avg_latency = total_latency / len(TEST_QUERIES)
    accuracy = total_correct / len(TEST_QUERIES) * 100
    
    print(f"Total queries: {len(TEST_QUERIES)}")
    print(f"Successful parses: {sum(1 for r in results if r['success'])}/{len(TEST_QUERIES)}")
    print(f"Correct intents: {total_correct}/{len(TEST_QUERIES)} ({accuracy:.1f}%)")
    print(f"Average latency: {avg_latency:.1f}ms")
    print(f"Min latency: {min(r['latency_ms'] for r in results):.1f}ms")
    print(f"Max latency: {max(r['latency_ms'] for r in results):.1f}ms")
    print()
    
    # Success criteria from ADR-005
    print("ADR-005 Success Criteria:")
    print(f"  Latency < 200ms: {'✓ PASS' if avg_latency < 200 else '✗ FAIL'} ({avg_latency:.1f}ms)")
    print(f"  JSON parsing: {'✓ PASS' if all(r['success'] for r in results) else '✗ PARTIAL'}")
    print(f"  Intent accuracy: {'✓ PASS' if accuracy >= 80 else '✗ FAIL'} ({accuracy:.1f}%)")


if __name__ == "__main__":
    main()
