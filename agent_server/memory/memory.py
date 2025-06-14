"""
Memory Module

This module is responsible for managing both long-term and short-term memory
for the agent system, including storing and retrieving information.
"""
from typing import Dict, List, Optional, Any, Union
import json
import os
import time
from datetime import datetime

class Memory:
    """
    Memory class for handling both long-term and short-term memory.
    """
    
    def __init__(self):
        """Initialize the memory module"""
        # Long-term memory store
        self.long_term_memory = {
            "retrieval_docs": {},
            "knowledge_database": {},
            "past_executions": [],
            "task_results": {}
        }
        
        # Short-term memory store
        self.short_term_memory = {
            "intermediate_outcomes": {},
            "recent_interactions": [],
            "context": {},
            "chat_history": []
        }
        
        # File path for persistent storage
        self.storage_path = os.path.join(os.getcwd(), "memory_storage.json")
        
        # Load existing memory if available
        self._load_memory()
    
    async def get(self, key: str, memory_type: str = "short_term") -> Optional[Any]:
        """
        Retrieve a value from memory.
        
        Args:
            key: The key to retrieve
            memory_type: The type of memory to access ("short_term" or "long_term")
        
        Returns:
            The value associated with the key, or None if not found
        """
        if memory_type == "short_term":
            # Try to get from specific short-term categories first
            for category in ["intermediate_outcomes", "context", "recent_interactions", "chat_history"]:
                if category == key:
                    return self.short_term_memory.get(category)
                if isinstance(self.short_term_memory.get(category), dict) and key in self.short_term_memory.get(category, {}):
                    return self.short_term_memory[category].get(key)
            
            # Check if it's a direct key in short_term_memory
            return self.short_term_memory.get(key)
        
        elif memory_type == "long_term":
            # Try to get from specific long-term categories first
            for category in ["retrieval_docs", "knowledge_database", "past_executions", "task_results"]:
                if category == key:
                    return self.long_term_memory.get(category)
                if isinstance(self.long_term_memory.get(category), dict) and key in self.long_term_memory.get(category, {}):
                    return self.long_term_memory[category].get(key)
            
            # Check if it's a direct key in long_term_memory
            return self.long_term_memory.get(key)
        
        return None
    
    async def set(self, key: str, value: Any, memory_type: str = "short_term") -> bool:
        """
        Store a value in memory.
        
        Args:
            key: The key to store
            value: The value to store
            memory_type: The type of memory to access ("short_term" or "long_term")
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if memory_type == "short_term":
                # Handle special keys
                if key == "context":
                    self.short_term_memory["context"].update(value if isinstance(value, dict) else {key: value})
                elif key == "chat_history":
                    if isinstance(value, list):
                        self.short_term_memory["chat_history"].extend(value)
                    else:
                        self.short_term_memory["chat_history"].append(value)
                elif key == "recent_interactions":
                    if isinstance(value, list):
                        self.short_term_memory["recent_interactions"].extend(value)
                    else:
                        self.short_term_memory["recent_interactions"].append(value)
                elif key == "intermediate_outcomes":
                    self.short_term_memory["intermediate_outcomes"].update(value if isinstance(value, dict) else {key: value})
                else:
                    # Direct key-value
                    self.short_term_memory[key] = value
            
            elif memory_type == "long_term":
                # Handle special keys
                if key == "task_results":
                    self.long_term_memory["task_results"].update(value if isinstance(value, dict) else {key: value})
                elif key == "past_executions":
                    if isinstance(value, list):
                        self.long_term_memory["past_executions"].extend(value)
                    else:
                        self.long_term_memory["past_executions"].append(value)
                elif key == "knowledge_database":
                    self.long_term_memory["knowledge_database"].update(value if isinstance(value, dict) else {key: value})
                elif key == "retrieval_docs":
                    self.long_term_memory["retrieval_docs"].update(value if isinstance(value, dict) else {key: value})
                else:
                    # Direct key-value
                    self.long_term_memory[key] = value
            
            # Save memory to storage
            self._save_memory()
            return True
        
        except Exception as e:
            print(f"Error setting memory: {str(e)}")
            return False
    
    async def clear_short_term(self) -> bool:
        """
        Clear short-term memory while preserving long-term memory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.short_term_memory = {
                "intermediate_outcomes": {},
                "recent_interactions": [],
                "context": {},
                "chat_history": []
            }
            self._save_memory()
            return True
        except Exception as e:
            print(f"Error clearing short-term memory: {str(e)}")
            return False
    
    # A2A Agent Support Methods
    async def store_agent_state(self, session_id: str, agent_name: str, state: Dict[str, Any]) -> None:
        """
        Store agent state for A2A agents.
        
        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            state: Agent state dictionary
        """
        key = f"agent_state_{session_id}_{agent_name}"
        await self.set(key, state, "short_term")
    
    async def store_agent_memory(
        self, 
        session_id: str, 
        agent_name: str, 
        memory_type: str, 
        key: str, 
        value: Any
    ) -> None:
        """
        Store agent memory for A2A agents.
        
        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            memory_type: Type of memory (working, long_term)
            key: Memory key
            value: Value to store
        """
        memory_key = f"agent_memory_{session_id}_{agent_name}_{memory_type}_{key}"
        storage_type = "long_term" if memory_type == "long_term" else "short_term"
        await self.set(memory_key, value, storage_type)
    
    async def retrieve_agent_state(self, session_id: str, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve agent state for A2A agents.
        
        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            
        Returns:
            Agent state dictionary or None
        """
        key = f"agent_state_{session_id}_{agent_name}"
        return await self.get(key, "short_term")
    
    async def retrieve_agent_memory(
        self, 
        session_id: str, 
        agent_name: str, 
        memory_type: str, 
        key: str
    ) -> Any:
        """
        Retrieve agent memory for A2A agents.
        
        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            memory_type: Type of memory (working, long_term)
            key: Memory key
            
        Returns:
            Stored value or None
        """
        memory_key = f"agent_memory_{session_id}_{agent_name}_{memory_type}_{key}"
        storage_type = "long_term" if memory_type == "long_term" else "short_term"
        return await self.get(memory_key, storage_type)
    
    async def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """
        Get keys matching a pattern for A2A agents.
        
        Args:
            pattern: Pattern to match (simple contains check)
            
        Returns:
            List of matching keys
        """
        matching_keys = []
        
        # Check short-term memory
        for key in self.short_term_memory.keys():
            if pattern.replace("*", "") in key:
                matching_keys.append(key)
        
        # Check long-term memory
        for key in self.long_term_memory.keys():
            if pattern.replace("*", "") in key:
                matching_keys.append(key)
        
        return matching_keys
    
    def _save_memory(self) -> None:
        """Save memory to persistent storage"""
        try:
            memory_data = {
                "long_term": self.long_term_memory,
                "short_term": self.short_term_memory,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {str(e)}")
    
    def _load_memory(self) -> None:
        """Load memory from persistent storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    memory_data = json.load(f)
                
                if "long_term" in memory_data:
                    self.long_term_memory = memory_data["long_term"]
                
                if "short_term" in memory_data:
                    self.short_term_memory = memory_data["short_term"]
        except Exception as e:
            print(f"Error loading memory: {str(e)}")
            # Continue with empty memory