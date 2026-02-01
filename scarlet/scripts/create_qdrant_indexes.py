"""
Create Qdrant Payload Indexes for Human-Like Memory v2.0

This script creates the necessary payload indexes for efficient filtering
as defined in ADR-005.

Run this ONCE after the collections exist.

Author: ABIOGENESIS Team
Date: 2026-02-01
ADR: ADR-005 Phase 1 - Step 1.3
"""

import logging
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Collections to index
COLLECTIONS = ["episodes", "concepts", "skills", "emotions"]

# Indexes to create per collection
# Format: (field_name, schema_type)
INDEXES = [
    # Temporal filters (ADR-005 Section 2.2)
    ("date", PayloadSchemaType.KEYWORD),           # "2026-02-01" - exact match
    ("time_of_day", PayloadSchemaType.KEYWORD),    # "morning|afternoon|evening|night"
    ("day_of_week", PayloadSchemaType.KEYWORD),    # "monday", "tuesday", etc.
    
    # Entity filters (ADR-005 Section 2.2)
    ("participants", PayloadSchemaType.KEYWORD),   # ["Davide", "Marco"]
    ("topics", PayloadSchemaType.KEYWORD),         # ["memoria", "architettura"]
    
    # Emotional filters (ADR-005 Section 2.2)
    ("emotional_valence", PayloadSchemaType.FLOAT),    # -1.0 to 1.0
    ("emotional_arousal", PayloadSchemaType.FLOAT),    # 0.0 to 1.0
    ("primary_emotion", PayloadSchemaType.KEYWORD),    # "curiosity", "joy", etc.
    
    # Importance/Decay filters (ADR-005 Section 2.2)
    ("importance", PayloadSchemaType.FLOAT),       # 0.0 to 1.0
    ("decay_factor", PayloadSchemaType.FLOAT),     # 0.0 to 1.0
    ("access_count", PayloadSchemaType.INTEGER),   # 0, 1, 2, ...
    
    # Relation filters (ADR-005 Section 2.2)
    ("related_entities", PayloadSchemaType.KEYWORD),   # For entity lookups
    ("related_topics", PayloadSchemaType.KEYWORD),     # For topic lookups
    
    # Meta filters
    ("type", PayloadSchemaType.KEYWORD),           # "episodic", "semantic", etc.
    ("source", PayloadSchemaType.KEYWORD),         # "conversation", "sleep_consolidation"
    ("session_id", PayloadSchemaType.KEYWORD),     # For session-based queries
    ("verified", PayloadSchemaType.BOOL),          # User-verified memories
]


def create_indexes():
    """Create all payload indexes for efficient filtering."""
    
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # Check connection
    try:
        collections = client.get_collections()
        existing_collections = [c.name for c in collections.collections]
        logger.info(f"Connected to Qdrant. Collections: {existing_collections}")
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return False
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for collection in COLLECTIONS:
        if collection not in existing_collections:
            logger.warning(f"Collection '{collection}' does not exist, skipping")
            continue
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Creating indexes for collection: {collection}")
        logger.info(f"{'='*50}")
        
        # Get existing indexes
        try:
            collection_info = client.get_collection(collection)
            existing_indexes = set(collection_info.payload_schema.keys()) if collection_info.payload_schema else set()
            logger.info(f"Existing indexes: {existing_indexes}")
        except Exception as e:
            logger.warning(f"Could not get existing indexes: {e}")
            existing_indexes = set()
        
        for field_name, schema_type in INDEXES:
            if field_name in existing_indexes:
                logger.info(f"  ⏭️  Index '{field_name}' already exists, skipping")
                skip_count += 1
                continue
            
            try:
                client.create_payload_index(
                    collection_name=collection,
                    field_name=field_name,
                    field_schema=schema_type,
                    wait=True
                )
                logger.info(f"  ✅ Created index '{field_name}' ({schema_type.name})")
                success_count += 1
            except Exception as e:
                # Some indexes may fail if field doesn't exist yet - that's OK
                logger.warning(f"  ⚠️  Could not create index '{field_name}': {e}")
                fail_count += 1
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("INDEX CREATION SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"✅ Created: {success_count}")
    logger.info(f"⏭️  Skipped (already exist): {skip_count}")
    logger.info(f"⚠️  Failed: {fail_count}")
    
    return True


def verify_indexes():
    """Verify all indexes exist."""
    
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    logger.info("\n" + "="*50)
    logger.info("INDEX VERIFICATION")
    logger.info("="*50)
    
    for collection in COLLECTIONS:
        try:
            collection_info = client.get_collection(collection)
            indexes = list(collection_info.payload_schema.keys()) if collection_info.payload_schema else []
            logger.info(f"\n{collection}:")
            logger.info(f"  Indexes: {indexes}")
            logger.info(f"  Count: {len(indexes)}")
        except Exception as e:
            logger.error(f"  Error: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Qdrant Payload Index Creator - ADR-005")
    print("="*60)
    print()
    
    create_indexes()
    verify_indexes()
