"""
Embedding Manager for Scarlet's Memory System

This module provides:
- Embedding generation using BGE-m3 (via Ollama)
- Fallback random embeddings for testing
- Caching and batching support

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-01-31
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_CACHE_SIZE = 1000


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    vector: List[float]
    model: str
    dimensions: int
    cached: bool = False
    generation_time_ms: float = 0.0


class EmbeddingManager:
    """
    Manager for generating text embeddings.
    
    Uses BGE-m3 via Ollama when available,
    falls back to deterministic pseudo-embeddings for testing.
    """
    
    def __init__(
        self,
        model: str = EMBEDDING_MODEL,
        ollama_url: str = OLLAMA_URL,
        use_cache: bool = True,
    ):
        """
        Initialize embedding manager.
        
        Args:
            model: Embedding model name
            ollama_url: Ollama server URL
            use_cache: Whether to cache embeddings
        """
        self.model = model
        self.ollama_url = ollama_url
        self.use_cache = use_cache
        
        # Cache for embeddings
        self._cache: Dict[str, EmbeddingResult] = {}
        self._cache_order: List[str] = []
        
        # Determine dimensions based on model
        self.dimensions = self._get_model_dimensions()
    
    def _get_model_dimensions(self) -> int:
        """Get embedding dimensions for model."""
        model_dims = {
            "bge-m3": 1024,
            "bge-large": 1024,
            "bge-base": 768,
            "nomic-embed-text": 768,
            "mxbai-embed-large": 1024,
        }
        return model_dims.get(self.model, 1024)
    
    def is_ollama_available(self) -> bool:
        """Check if Ollama is available for embeddings."""
        try:
            import httpx
            response = httpx.get(f"{OLLAMA_URL}/api/version", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
    
    def _get_text_hash(self, text: str) -> str:
        """Get deterministic hash for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _get_deterministic_embedding(self, text: str, dimensions: int) -> List[float]:
        """
        Generate a deterministic pseudo-embedding for text.
        
        Used for testing when Ollama is not available.
        The same text will always produce the same embedding.
        """
        import random
        
        # Create a seed from the text
        text_hash = self._get_text_hash(text)
        seed = int(text_hash[:8], 16) % (2**31)
        
        # Generate deterministic random values
        random.seed(seed)
        vector = [random.uniform(-1, 1) for _ in range(dimensions)]
        
        # Normalize
        magnitude = sum(v**2 for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        
        return vector
    
    def generate(
        self,
        text: str,
        dimensions: Optional[int] = None,
        normalize: bool = True,
    ) -> EmbeddingResult:
        """
        Generate embedding for a text.
        
        Args:
            text: Text to embed
            dimensions: Override dimensions (None = use model default)
            normalize: Whether to normalize output vector
            
        Returns:
            EmbeddingResult with vector and metadata
        """
        import time
        start_time = time.time()
        
        dims = dimensions or self.dimensions
        
        # Check cache
        cache_key = f"{text[:100]}:{dims}"
        if self.use_cache and cache_key in self._cache:
            result = self._cache[cache_key]
            result.cached = True
            result.generation_time_ms = (time.time() - start_time) * 1000
            return result
        
        # Try Ollama if available
        if self.is_ollama_available():
            try:
                vector = self._generate_from_ollama(text, dims)
                result = EmbeddingResult(
                    vector=vector,
                    model=self.model,
                    dimensions=dims,
                    cached=False,
                    generation_time_ms=(time.time() - start_time) * 1000,
                )
            except Exception as e:
                print(f"[EmbeddingManager] Ollama failed: {e}, using fallback")
                vector = self._get_deterministic_embedding(text, dims)
                result = EmbeddingResult(
                    vector=vector,
                    model="fallback",
                    dimensions=dims,
                    cached=False,
                    generation_time_ms=(time.time() - start_time) * 1000,
                )
        else:
            # Use deterministic fallback
            vector = self._get_deterministic_embedding(text, dims)
            result = EmbeddingResult(
                vector=vector,
                model="fallback",
                dimensions=dims,
                cached=False,
                generation_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Normalize if requested
        if normalize and vector:
            magnitude = sum(v**2 for v in vector) ** 0.5
            if magnitude > 0:
                vector = [v / magnitude for v in vector]
        
        result.vector = vector
        
        # Add to cache
        if self.use_cache:
            self._cache[cache_key] = result
            self._cache_order.append(cache_key)
            
            # LRU eviction
            while len(self._cache_order) > EMBEDDING_CACHE_SIZE:
                old_key = self._cache_order.pop(0)
                if old_key in self._cache:
                    del self._cache[old_key]
        
        return result
    
    def _generate_from_ollama(self, text: str, dimensions: int) -> List[float]:
        """Generate embedding using Ollama API."""
        import httpx
        import json
        
        response = httpx.post(
            f"{OLLAMA_URL}/api/embed",
            json={
                "model": self.model,
                "input": text,
            },
            timeout=60.0,
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.status_code}")
        
        data = response.json()
        
        # Handle different response formats
        if "embeddings" in data:
            embeddings = data["embeddings"]
        elif "embedding" in data:
            embeddings = [data["embedding"]]
        else:
            raise ValueError(f"Unexpected Ollama response: {data.keys()}")
        
        if not embeddings:
            raise ValueError("No embeddings in response")
        
        vector = embeddings[0]
        
        # Handle different vector formats
        if isinstance(vector, list):
            # Normalize if needed
            magnitude = sum(v**2 for v in vector) ** 0.5
            if magnitude > 0 and len(vector) != dimensions:
                # Truncate or pad
                if len(vector) > dimensions:
                    vector = vector[:dimensions]
                else:
                    vector = vector + [0.0] * (dimensions - len(vector))
        
        return vector
    
    def generate_batch(
        self,
        texts: List[str],
        dimensions: Optional[int] = None,
        show_progress: bool = False,
    ) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            dimensions: Override dimensions
            show_progress: Show progress indicator
            
        Returns:
            List of EmbeddingResult objects
        """
        results = []
        for i, text in enumerate(texts):
            if show_progress and i % 10 == 0:
                print(f"Embedding {i}/{len(texts)}...")
            results.append(self.generate(text, dimensions))
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics."""
        return {
            "cache_size": len(self._cache),
            "cache_hits": sum(1 for r in self._cache.values() if r.cached),
            "model": self.model,
            "dimensions": self.dimensions,
            "ollama_available": self.is_ollama_available(),
        }
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()
        self._cache_order.clear()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.clear_cache()


# Convenience function
def get_embedding_manager() -> EmbeddingManager:
    """Get a configured embedding manager instance."""
    return EmbeddingManager()


# For quick testing
if __name__ == "__main__":
    import sys
    
    manager = EmbeddingManager()
    
    print(f"Model: {manager.model}")
    print(f"Dimensions: {manager.dimensions}")
    print(f"Ollama available: {manager.is_ollama_available()}")
    print()
    
    # Test embedding
    test_texts = [
        "This is a test sentence",
        "Another example for embedding",
        "Machine learning and AI are fascinating",
    ]
    
    for text in test_texts:
        result = manager.generate(text)
        print(f"Text: {text[:40]}...")
        print(f"  Vector: {len(result.vector)} dims, cached={result.cached}, time={result.generation_time_ms:.2f}ms")
        print()
