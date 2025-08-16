"""Episodic memory system for SEFAS agents."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import numpy as np
from collections import deque
import hashlib

class EpisodicMemory:
    """Simple episodic memory for agent experiences"""
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.memories: deque = deque(maxlen=capacity)
        self.index = {}  # Simple string-based index
        
    def add(self, memory: Dict[str, Any]) -> None:
        """Add a memory to the episodic store"""
        
        # Add timestamp if not present
        if 'timestamp' not in memory:
            memory['timestamp'] = datetime.now().isoformat()
        
        # Create memory hash for deduplication
        memory_hash = self._hash_memory(memory)
        
        # Check if similar memory already exists
        if memory_hash not in self.index:
            self.memories.append(memory)
            self.index[memory_hash] = len(self.memories) - 1
        
    def get_relevant(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Get k most relevant memories for a query"""
        
        if not self.memories:
            return []
        
        # Simple relevance scoring based on keyword overlap
        scored_memories = []
        query_words = set(query.lower().split())
        
        for memory in self.memories:
            score = self._calculate_relevance(memory, query_words)
            scored_memories.append((score, memory))
        
        # Sort by relevance and return top k
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:k]]
    
    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get n most recent memories"""
        return list(self.memories)[-n:]
    
    def get_by_type(self, memory_type: str) -> List[Dict[str, Any]]:
        """Get memories by type"""
        return [
            memory for memory in self.memories 
            if memory.get('type') == memory_type
        ]
    
    def consolidate(self) -> Dict[str, Any]:
        """Consolidate memories into patterns"""
        
        if len(self.memories) < 5:
            return {"status": "insufficient_data"}
        
        # Group memories by task type
        task_types = {}
        confidence_scores = []
        
        for memory in self.memories:
            task_type = memory.get('task', {}).get('type', 'general')
            if task_type not in task_types:
                task_types[task_type] = []
            task_types[task_type].append(memory)
            
            confidence = memory.get('confidence', 0.5)
            confidence_scores.append(confidence)
        
        # Calculate patterns
        patterns = {}
        for task_type, memories in task_types.items():
            avg_confidence = np.mean([m.get('confidence', 0.5) for m in memories])
            patterns[task_type] = {
                'count': len(memories),
                'avg_confidence': avg_confidence,
                'trend': 'improving' if avg_confidence > 0.6 else 'needs_work'
            }
        
        return {
            'status': 'consolidated',
            'total_memories': len(self.memories),
            'avg_confidence': np.mean(confidence_scores),
            'patterns': patterns,
            'consolidation_time': datetime.now().isoformat()
        }
    
    def _hash_memory(self, memory: Dict[str, Any]) -> str:
        """Create hash for memory deduplication"""
        
        # Create simplified version for hashing
        hashable_content = {
            'task_desc': str(memory.get('task', {}).get('description', '')),
            'response_content': str(memory.get('response', {}).get('proposal', ''))[:200]
        }
        
        content_str = json.dumps(hashable_content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _calculate_relevance(self, memory: Dict[str, Any], query_words: set) -> float:
        """Calculate relevance score between memory and query"""
        
        # Extract text from memory
        memory_text = ""
        
        if 'task' in memory:
            memory_text += str(memory['task'].get('description', ''))
        
        if 'response' in memory:
            memory_text += str(memory['response'].get('proposal', ''))
            memory_text += str(memory['response'].get('reasoning', ''))
        
        memory_words = set(memory_text.lower().split())
        
        # Calculate overlap
        if not memory_words:
            return 0.0
        
        overlap = len(query_words & memory_words)
        relevance = overlap / len(query_words) if query_words else 0.0
        
        # Boost recent memories
        try:
            memory_time = datetime.fromisoformat(memory.get('timestamp', ''))
            hours_ago = (datetime.now() - memory_time).total_seconds() / 3600
            recency_boost = max(0, 1.0 - (hours_ago / 24))  # Boost for last 24 hours
            relevance += recency_boost * 0.1
        except:
            pass
        
        # Boost high-confidence memories
        confidence = memory.get('confidence', 0.5)
        relevance += confidence * 0.1
        
        return min(relevance, 1.0)  # Cap at 1.0
    
    def clear(self) -> None:
        """Clear all memories"""
        self.memories.clear()
        self.index.clear()
    
    def size(self) -> int:
        """Get current memory count"""
        return len(self.memories)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export memories to dictionary"""
        return {
            'memories': list(self.memories),
            'capacity': self.capacity,
            'count': len(self.memories)
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load memories from dictionary"""
        self.capacity = data.get('capacity', 100)
        self.memories = deque(data.get('memories', []), maxlen=self.capacity)
        
        # Rebuild index
        self.index = {}
        for i, memory in enumerate(self.memories):
            memory_hash = self._hash_memory(memory)
            self.index[memory_hash] = i