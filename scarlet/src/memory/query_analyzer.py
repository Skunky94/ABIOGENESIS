"""
Query Analyzer for Human-Like Memory System v2.0

Analyzes user queries to determine optimal retrieval strategy using
a local LLM (qwen2.5:1.5b) on Ollama.

Features:
- Intent detection (temporal, entity, emotional, topic, procedural, general)
- Time reference resolution (yesterday, last week, etc.)
- Entity extraction (people, things mentioned)
- Topic extraction
- Emotion filter detection

Author: ABIOGENESIS Team
Date: 2026-02-01
ADR: ADR-005 Phase 2
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Types of query intents for memory retrieval"""
    TEMPORAL = "temporal"       # "Cosa abbiamo fatto ieri?"
    ENTITY = "entity"           # "Cosa sai di Davide?"
    EMOTIONAL = "emotional"     # "Cosa ti è piaciuto?"
    TOPIC = "topic"             # "Parlami di ABIOGENESIS"
    PROCEDURAL = "procedural"   # "Come si fa X?"
    GENERAL = "general"         # Default fallback


class TimeType(Enum):
    """Types of time references"""
    EXACT = "exact"         # "il 15 gennaio"
    RANGE = "range"         # "questa settimana"
    RELATIVE = "relative"   # "ieri", "3 giorni fa"
    NONE = "none"           # No time reference


@dataclass
class TimeReference:
    """Resolved time reference from query"""
    type: TimeType
    reference: Optional[str] = None          # Original reference ("ieri")
    resolved_start: Optional[datetime] = None  # Resolved start datetime
    resolved_end: Optional[datetime] = None    # Resolved end datetime
    
    def to_date_filter(self) -> Optional[str]:
        """Get date string for Qdrant filter (YYYY-MM-DD)"""
        if self.resolved_start:
            return self.resolved_start.strftime("%Y-%m-%d")
        return None
    
    def to_date_range(self) -> tuple[Optional[str], Optional[str]]:
        """Get date range for Qdrant filter"""
        start = self.resolved_start.strftime("%Y-%m-%d") if self.resolved_start else None
        end = self.resolved_end.strftime("%Y-%m-%d") if self.resolved_end else None
        return (start, end)


@dataclass
class QueryAnalysis:
    """Result of query analysis"""
    # Primary intent
    intent: QueryIntent
    
    # Time information
    time: TimeReference
    
    # Extracted entities
    entities: List[str] = field(default_factory=list)
    
    # Extracted topics
    topics: List[str] = field(default_factory=list)
    
    # Emotion filter
    emotion_filter: Optional[str] = None  # "positive", "negative", "neutral"
    
    # Memory types to search
    memory_types: List[str] = field(default_factory=lambda: ["episodic", "semantic", "procedural", "emotional"])
    
    # Clean query for semantic search
    semantic_query: Optional[str] = None
    
    # Confidence score
    confidence: float = 0.0
    
    # Raw LLM response (for debugging)
    raw_response: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "intent": self.intent.value,
            "time": {
                "type": self.time.type.value,
                "reference": self.time.reference,
                "start": self.time.resolved_start.isoformat() if self.time.resolved_start else None,
                "end": self.time.resolved_end.isoformat() if self.time.resolved_end else None,
            },
            "entities": self.entities,
            "topics": self.topics,
            "emotion_filter": self.emotion_filter,
            "memory_types": self.memory_types,
            "semantic_query": self.semantic_query,
            "confidence": self.confidence,
        }


@dataclass
class QueryAnalyzerConfig:
    """Configuration for Query Analyzer"""
    ollama_url: str = "http://localhost:11434"
    model: str = "qwen2.5:1.5b"
    temperature: float = 0.1
    max_tokens: int = 300
    timeout: float = 30.0
    
    @classmethod
    def from_env(cls) -> "QueryAnalyzerConfig":
        return cls(
            ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            model=os.getenv("QUERY_ANALYZER_MODEL", "qwen2.5:1.5b"),
            temperature=float(os.getenv("QUERY_ANALYZER_TEMP", "0.1")),
            max_tokens=int(os.getenv("QUERY_ANALYZER_MAX_TOKENS", "300")),
            timeout=float(os.getenv("QUERY_ANALYZER_TIMEOUT", "30.0")),
        )


# System prompt for query analysis
QUERY_ANALYZER_PROMPT = """Sei un analizzatore di query per un sistema di memoria AI chiamato Scarlet.
Il tuo compito è analizzare la richiesta dell'utente e determinare la strategia di ricerca ottimale.

Data odierna: {today}
Ora corrente: {current_time}

REGOLE DI ANALISI:

1. INTENT (scegli UNO):
   - "temporal": domande su QUANDO ("ieri", "la settimana scorsa", "oggi")
   - "entity": domande su CHI/COSA ("cosa sai di Davide", "parlami di Marco")
   - "emotional": domande su EMOZIONI ("cosa ti è piaciuto", "cosa ti ha fatto arrabbiare")
   - "topic": domande su ARGOMENTI ("parlami di X", "cosa sai sull'AI")
   - "procedural": domande su COME FARE ("come si fa", "come funziona")
   - "general": tutto il resto (saluti, domande generiche)

2. TEMPO (risolvi riferimenti):
   - "ieri" = giorno prima di oggi
   - "oggi" = data odierna
   - "l'altro ieri" = 2 giorni fa
   - "settimana scorsa" = ultimi 7 giorni
   - "mese scorso" = ultimi 30 giorni
   - "3 giorni fa" = data specifica

3. ENTITÀ:
   - Estrai nomi di PERSONE menzionate (Davide, Marco, etc.)
   - Estrai nomi di COSE/PROGETTI specifici (ABIOGENESIS, Scarlet)

4. TOPICS:
   - Estrai argomenti generali discussi (memoria, architettura, AI, etc.)

5. EMOZIONI:
   - Se la query chiede emozioni positive -> "positive"
   - Se la query chiede emozioni negative -> "negative"
   - Altrimenti -> null

Rispondi SOLO con JSON valido nel seguente formato (niente altro testo):
{{
    "intent": "temporal|entity|emotional|topic|procedural|general",
    "time_type": "exact|range|relative|none",
    "time_reference": "testo originale o null",
    "time_start": "YYYY-MM-DD o null",
    "time_end": "YYYY-MM-DD o null",
    "entities": ["lista", "di", "entità"],
    "topics": ["lista", "di", "argomenti"],
    "emotion_filter": "positive|negative|neutral|null",
    "semantic_query": "query pulita per ricerca semantica"
}}"""


class QueryAnalyzer:
    """
    Analyzes user queries to determine optimal memory retrieval strategy.
    
    Uses a local LLM (qwen2.5:1.5b) via Ollama for intent detection,
    entity extraction, and time reference resolution.
    """
    
    def __init__(self, config: Optional[QueryAnalyzerConfig] = None):
        """
        Initialize Query Analyzer.
        
        Args:
            config: Configuration for analyzer. If None, loads from environment.
        """
        self.config = config or QueryAnalyzerConfig.from_env()
        self._client = httpx.Client(timeout=self.config.timeout)
        logger.info(f"QueryAnalyzer initialized with model: {self.config.model}")
    
    def analyze(self, query: str, known_entities: Optional[List[str]] = None) -> QueryAnalysis:
        """
        Analyze a user query to determine retrieval strategy.
        
        Args:
            query: The user's query text
            known_entities: Optional list of known entities for context
            
        Returns:
            QueryAnalysis object with intent, time, entities, etc.
        """
        if not query or not query.strip():
            return self._default_analysis("")
        
        # Build prompt
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        
        prompt = QUERY_ANALYZER_PROMPT.format(
            today=today,
            current_time=current_time,
        )
        
        # Add known entities if provided
        if known_entities:
            prompt += f"\n\nEntità conosciute: {', '.join(known_entities)}"
        
        full_prompt = f"{prompt}\n\nQuery utente: \"{query}\"\n\nJSON:"
        
        try:
            # Call Ollama
            response = self._client.post(
                f"{self.config.ollama_url}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    }
                }
            )
            response.raise_for_status()
            
            result = response.json()
            raw_response = result.get("response", "")
            
            # Parse JSON from response
            analysis = self._parse_response(raw_response, query)
            analysis.raw_response = raw_response
            
            logger.debug(f"Query analyzed: intent={analysis.intent.value}, entities={analysis.entities}")
            return analysis
            
        except httpx.TimeoutException:
            logger.warning(f"Query analysis timed out, using default")
            return self._default_analysis(query)
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return self._default_analysis(query)
    
    def _parse_response(self, raw_response: str, original_query: str) -> QueryAnalysis:
        """Parse LLM response into QueryAnalysis object."""
        try:
            # Find JSON in response
            json_start = raw_response.find("{")
            json_end = raw_response.rfind("}") + 1
            
            if json_start < 0 or json_end <= json_start:
                logger.warning("No JSON found in response")
                return self._default_analysis(original_query)
            
            json_str = raw_response[json_start:json_end]
            data = json.loads(json_str)
            
            # Parse intent
            intent_str = data.get("intent", "general").lower()
            try:
                intent = QueryIntent(intent_str)
            except ValueError:
                intent = QueryIntent.GENERAL
            
            # Parse time
            time_type_str = data.get("time_type", "none").lower()
            try:
                time_type = TimeType(time_type_str)
            except ValueError:
                time_type = TimeType.NONE
            
            time_ref = TimeReference(
                type=time_type,
                reference=data.get("time_reference"),
                resolved_start=self._parse_date(data.get("time_start")),
                resolved_end=self._parse_date(data.get("time_end")),
            )
            
            # Parse other fields
            entities = data.get("entities", [])
            if isinstance(entities, str):
                entities = [entities] if entities else []
            entities = [e for e in entities if e and e.lower() not in ("null", "none", "")]
            
            topics = data.get("topics", [])
            if isinstance(topics, str):
                topics = [topics] if topics else []
            topics = [t for t in topics if t and t.lower() not in ("null", "none", "")]
            
            emotion_filter = data.get("emotion_filter")
            if emotion_filter and emotion_filter.lower() in ("null", "none"):
                emotion_filter = None
            
            semantic_query = data.get("semantic_query") or original_query
            
            # Determine memory types based on intent
            memory_types = self._get_memory_types(intent)
            
            return QueryAnalysis(
                intent=intent,
                time=time_ref,
                entities=entities,
                topics=topics,
                emotion_filter=emotion_filter,
                memory_types=memory_types,
                semantic_query=semantic_query,
                confidence=0.85,  # Based on test results
            )
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            return self._default_analysis(original_query)
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str or date_str.lower() in ("null", "none"):
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None
    
    def _get_memory_types(self, intent: QueryIntent) -> List[str]:
        """Determine which memory types to search based on intent."""
        if intent == QueryIntent.PROCEDURAL:
            return ["skills", "semantic"]
        elif intent == QueryIntent.EMOTIONAL:
            return ["emotions", "episodic"]
        elif intent == QueryIntent.ENTITY:
            return ["semantic", "episodic"]
        elif intent == QueryIntent.TEMPORAL:
            return ["episodic"]
        else:
            return ["episodic", "semantic", "skills", "emotions"]
    
    def _default_analysis(self, query: str) -> QueryAnalysis:
        """Return default analysis for fallback."""
        return QueryAnalysis(
            intent=QueryIntent.GENERAL,
            time=TimeReference(type=TimeType.NONE),
            entities=[],
            topics=[],
            emotion_filter=None,
            memory_types=["episodic", "semantic", "skills", "emotions"],
            semantic_query=query,
            confidence=0.0,
        )
    
    def close(self):
        """Close HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Singleton instance for reuse
_analyzer_instance: Optional[QueryAnalyzer] = None


def get_query_analyzer() -> QueryAnalyzer:
    """Get or create singleton QueryAnalyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = QueryAnalyzer()
    return _analyzer_instance


def analyze_query(query: str, known_entities: Optional[List[str]] = None) -> QueryAnalysis:
    """
    Convenience function to analyze a query.
    
    Args:
        query: The user's query text
        known_entities: Optional list of known entities for context
        
    Returns:
        QueryAnalysis object
    """
    analyzer = get_query_analyzer()
    return analyzer.analyze(query, known_entities)


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    test_queries = [
        "Cosa abbiamo fatto ieri?",
        "Cosa sai di Davide?",
        "Cosa ti è piaciuto della nostra conversazione?",
        "Parlami di ABIOGENESIS",
        "Come si fa a cercare nella memoria?",
        "Ciao, come stai?",
    ]
    
    analyzer = QueryAnalyzer()
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        result = analyzer.analyze(query)
        print(f"  Intent: {result.intent.value}")
        print(f"  Time: {result.time.type.value} ({result.time.reference})")
        print(f"  Entities: {result.entities}")
        print(f"  Topics: {result.topics}")
        print(f"  Emotion: {result.emotion_filter}")
        print(f"  Memory Types: {result.memory_types}")
