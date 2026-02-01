"""
Memory Enrichment Module (ADR-005)

Automatic extraction of:
- Entities (participants, proper nouns)
- Topics (key subjects)
- Emotions (valence, arousal, primary emotion)
- Temporal metadata (date, time_of_day, day_of_week)

Uses local qwen2.5:1.5b model via Ollama for zero cloud dependency.

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-02-01
"""

import os
import json
import httpx
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
ENRICHMENT_MODEL = os.getenv("ENRICHMENT_MODEL", "qwen2.5:1.5b")


@dataclass
class EnrichmentResult:
    """Result of memory enrichment analysis."""
    # Entities
    participants: List[str]         # People/entities mentioned
    topics: List[str]               # Key topics
    
    # Emotional analysis
    emotional_valence: float        # -1.0 to +1.0
    emotional_arousal: float        # 0.0 to 1.0
    primary_emotion: Optional[str]  # joy, sadness, fear, anger, surprise, neutral
    
    # Importance estimation
    importance: float               # 0.0 to 1.0
    
    # Temporal context
    date: str                       # ISO date YYYY-MM-DD
    time_of_day: str                # morning, afternoon, evening, night
    day_of_week: int                # 0=Monday, 6=Sunday
    
    # Extraction confidence
    confidence: float = 0.8


class MemoryEnrichment:
    """
    Enriches memory content with extracted metadata.
    
    Uses local LLM to analyze text and extract:
    - Named entities (people, places, organizations)
    - Topics and themes
    - Emotional content
    - Importance indicators
    """
    
    EXTRACTION_PROMPT = """Analyze this text and extract structured information.

TEXT:
{text}

Extract the following in JSON format:
{{
    "participants": ["list of people/entities mentioned"],
    "topics": ["list of key topics/subjects"],
    "emotional_valence": 0.0,  // -1.0 (very negative) to +1.0 (very positive)
    "emotional_arousal": 0.5,  // 0.0 (calm) to 1.0 (excited/intense)
    "primary_emotion": "neutral",  // joy, sadness, fear, anger, surprise, disgust, neutral
    "importance": 0.5  // 0.0 (trivial) to 1.0 (critical)
}}

Rules:
- participants: Extract any person names, organizations, or significant entities
- topics: Main subjects being discussed (max 5)
- emotional_valence: Overall positive/negative tone
- emotional_arousal: Level of emotional intensity
- primary_emotion: The dominant emotion
- importance: How significant is this information? (decisions=high, casual chat=low)

Respond ONLY with valid JSON, no explanation."""

    def __init__(self, model: str = None, ollama_url: str = None):
        """Initialize enrichment module."""
        self.model = model or ENRICHMENT_MODEL
        self.ollama_url = ollama_url or OLLAMA_URL
        self._client = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=30.0)
        return self._client
    
    def _get_temporal_metadata(self) -> Tuple[str, str, int]:
        """
        Get current temporal context.
        
        Returns:
            Tuple of (date, time_of_day, day_of_week)
        """
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        day_of_week = now.weekday()  # 0=Monday
        
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        return date, time_of_day, day_of_week
    
    def _call_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Call local LLM for extraction.
        
        Args:
            text: Text to analyze
            
        Returns:
            Parsed JSON response or None
        """
        prompt = self.EXTRACTION_PROMPT.format(text=text[:2000])  # Limit length
        
        try:
            client = self._get_client()
            response = client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 500
                    }
                }
            )
            response.raise_for_status()
            
            result = response.json()
            raw_response = result.get("response", "")
            
            # Parse JSON from response
            return self._parse_json(raw_response)
            
        except Exception as e:
            print(f"[MemoryEnrichment] LLM call failed: {e}")
            return None
    
    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response."""
        # Try direct parse first
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                try:
                    return json.loads(text[start:end].strip())
                except json.JSONDecodeError:
                    pass
        
        # Try to find JSON object
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        
        return None
    
    def enrich(self, text: str, existing_metadata: Dict[str, Any] = None) -> EnrichmentResult:
        """
        Enrich text with extracted metadata.
        
        Args:
            text: The text content to analyze
            existing_metadata: Optional existing metadata to preserve
            
        Returns:
            EnrichmentResult with extracted information
        """
        # Get temporal context
        date, time_of_day, day_of_week = self._get_temporal_metadata()
        
        # Try LLM extraction
        llm_result = self._call_llm(text)
        
        if llm_result:
            return EnrichmentResult(
                participants=llm_result.get("participants", []),
                topics=llm_result.get("topics", []),
                emotional_valence=float(llm_result.get("emotional_valence", 0.0)),
                emotional_arousal=float(llm_result.get("emotional_arousal", 0.5)),
                primary_emotion=llm_result.get("primary_emotion", "neutral"),
                importance=float(llm_result.get("importance", 0.5)),
                date=date,
                time_of_day=time_of_day,
                day_of_week=day_of_week,
                confidence=0.85
            )
        else:
            # Fallback to heuristics
            return self._fallback_enrichment(text, date, time_of_day, day_of_week)
    
    def _fallback_enrichment(
        self, 
        text: str, 
        date: str, 
        time_of_day: str, 
        day_of_week: int
    ) -> EnrichmentResult:
        """
        Fallback enrichment using simple heuristics.
        
        Used when LLM is unavailable.
        """
        # Simple heuristics
        text_lower = text.lower()
        
        # Emotional heuristics
        positive_words = ["happy", "great", "excellent", "love", "wonderful", "amazing", "felice", "bene", "ottimo"]
        negative_words = ["sad", "bad", "terrible", "hate", "awful", "angry", "triste", "male", "terribile"]
        
        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)
        
        if positive_count > negative_count:
            valence = min(0.5 + positive_count * 0.1, 1.0)
            emotion = "joy"
        elif negative_count > positive_count:
            valence = max(-0.5 - negative_count * 0.1, -1.0)
            emotion = "sadness"
        else:
            valence = 0.0
            emotion = "neutral"
        
        # Importance heuristics
        importance_indicators = ["important", "critical", "decision", "remember", "importante", "critico", "decisione"]
        importance = 0.5 + sum(0.1 for w in importance_indicators if w in text_lower)
        importance = min(importance, 1.0)
        
        return EnrichmentResult(
            participants=[],  # Can't extract without NER
            topics=[],
            emotional_valence=valence,
            emotional_arousal=0.5,
            primary_emotion=emotion,
            importance=importance,
            date=date,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            confidence=0.3  # Low confidence for heuristics
        )
    
    def enrich_dict(self, text: str, base_payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enrich and return as dictionary for Qdrant payload.
        
        Args:
            text: Text to analyze
            base_payload: Optional base payload to merge with
            
        Returns:
            Dictionary suitable for Qdrant point payload
        """
        result = self.enrich(text)
        
        enriched = {
            "participants": result.participants,
            "topics": result.topics,
            "emotional_valence": result.emotional_valence,
            "emotional_arousal": result.emotional_arousal,
            "primary_emotion": result.primary_emotion,
            "importance": result.importance,
            "date": result.date,
            "time_of_day": result.time_of_day,
            "day_of_week": result.day_of_week,
            "enrichment_confidence": result.confidence,
            "decay_factor": 1.0,  # Initialize decay
            "access_count": 0,
            "last_accessed": datetime.now().isoformat(),
        }
        
        if base_payload:
            # Merge with base, enriched values take precedence for new fields
            merged = {**base_payload, **enriched}
            return merged
        
        return enriched


# Singleton instance
_enrichment_instance: Optional[MemoryEnrichment] = None


def get_enrichment() -> MemoryEnrichment:
    """Get singleton MemoryEnrichment instance."""
    global _enrichment_instance
    if _enrichment_instance is None:
        _enrichment_instance = MemoryEnrichment()
    return _enrichment_instance


def enrich_memory(text: str, base_payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience function to enrich memory content.
    
    Args:
        text: Text to analyze
        base_payload: Optional base payload
        
    Returns:
        Enriched payload dictionary
    """
    return get_enrichment().enrich_dict(text, base_payload)
