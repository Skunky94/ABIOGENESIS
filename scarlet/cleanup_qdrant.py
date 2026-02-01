"""
Cleanup script per Qdrant collections.
Rimuove duplicati, test data, e rumore.

Usage: python cleanup_qdrant.py
"""

import requests
from collections import defaultdict

QDRANT_URL = "http://localhost:6333"

def get_all_points(collection: str) -> list:
    """Get all points from a collection."""
    resp = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/scroll",
        json={"limit": 100, "with_payload": True}
    )
    return resp.json().get("result", {}).get("points", [])

def delete_points(collection: str, ids: list) -> bool:
    """Delete points by IDs."""
    if not ids:
        return True
    resp = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/delete",
        json={"points": ids}
    )
    return resp.status_code == 200

def analyze_and_clean_collection(collection: str) -> dict:
    """Analyze and clean a collection."""
    print(f"\n{'='*60}")
    print(f"Analyzing: {collection}")
    print(f"{'='*60}")
    
    points = get_all_points(collection)
    print(f"Total points: {len(points)}")
    
    to_delete = []
    seen_titles = {}
    
    for p in points:
        pid = p["id"]
        payload = p.get("payload", {})
        title = payload.get("title", "")
        content = payload.get("content", "")
        ptype = payload.get("type", "")
        
        # 1. Delete test data
        if ptype == "test" or title == "" or title is None:
            print(f"  [DELETE] Test/Empty: {pid[:8]}...")
            to_delete.append(pid)
            continue
        
        # 2. Delete error messages saved as memory
        if "Error getting" in content or "Error" in title and len(content) < 50:
            print(f"  [DELETE] Error: {pid[:8]}... - {title[:30]}")
            to_delete.append(pid)
            continue
        
        # 3. Delete generic test strings
        test_patterns = ["Quick test", "High importance test", "test", "Test Memory Integration"]
        if any(pat.lower() in title.lower() for pat in test_patterns) and len(content) < 100:
            print(f"  [DELETE] Test pattern: {pid[:8]}... - {title[:30]}")
            to_delete.append(pid)
            continue
        
        # 4. Delete duplicates (keep first occurrence)
        title_key = title.strip().lower()
        if title_key in seen_titles:
            print(f"  [DELETE] Duplicate: {pid[:8]}... - {title[:30]}")
            to_delete.append(pid)
        else:
            seen_titles[title_key] = pid
            print(f"  [KEEP] {pid[:8]}... - {title[:40]}")
    
    # Summary
    keep_count = len(points) - len(to_delete)
    print(f"\nSummary for {collection}:")
    print(f"  - Original: {len(points)}")
    print(f"  - To delete: {len(to_delete)}")
    print(f"  - Will keep: {keep_count}")
    
    return {
        "collection": collection,
        "original": len(points),
        "to_delete": to_delete,
        "keep": keep_count
    }

def main():
    print("=" * 60)
    print("QDRANT COLLECTION CLEANUP")
    print("=" * 60)
    
    collections = ["episodes", "concepts", "skills"]  # Skip emotions (different vector size)
    
    results = []
    for col in collections:
        result = analyze_and_clean_collection(col)
        results.append(result)
    
    # Ask for confirmation
    total_delete = sum(len(r["to_delete"]) for r in results)
    print(f"\n{'='*60}")
    print(f"TOTAL TO DELETE: {total_delete} points")
    print(f"{'='*60}")
    
    confirm = input("\nProceed with deletion? (yes/no): ")
    
    if confirm.lower() == "yes":
        for r in results:
            if r["to_delete"]:
                success = delete_points(r["collection"], r["to_delete"])
                status = "✓" if success else "✗"
                print(f"{status} Deleted {len(r['to_delete'])} from {r['collection']}")
        print("\nCleanup complete!")
    else:
        print("Cleanup cancelled.")

if __name__ == "__main__":
    main()
