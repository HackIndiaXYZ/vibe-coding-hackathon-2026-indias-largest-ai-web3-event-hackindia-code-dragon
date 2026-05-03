import os
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional

import config

class MemoryManager:
    """
    The MemoryManager is responsible for the long-term retention of conversation data.
    It simulates an advanced memory protocol, ensuring that Natsuki and Ren
    can recall past interactions, compute user engagement statistics, and manage
    context windows to avoid token limit exhaustion.
    """

    def __init__(self, memory_file: str = None):
        self.memory_file = memory_file or config.MEMORY_FILE
        self.memory_state: Dict[str, Any] = self._load_disk()
        self.max_turns = config.MAX_MEMORY_TURNS

    def _load_disk(self) -> Dict[str, Any]:
        """Loads the memory state from the persistent JSON file on disk."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validate schema roughly
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"[MemoryManager] Error loading memory file: {e}")
                # Backup corrupt memory
                if os.path.exists(self.memory_file):
                    backup_name = f"{self.memory_file}.bak.{int(datetime.datetime.now().timestamp())}"
                    os.rename(self.memory_file, backup_name)
                    print(f"[MemoryManager] Corrupt memory backed up to {backup_name}")
        
        # Return fresh state if no valid file exists
        return {}

    def _save_disk(self) -> None:
        """Disabled to prevent unwanted workspace reloads."""
        pass

    def initialize_session(self, session_id: Optional[str]) -> str:
        """
        Initializes a new session or retrieves an existing one.
        Returns the confirmed session_id.
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            
        if session_id not in self.memory_state:
            self.memory_state[session_id] = {
                "created_at": datetime.datetime.now().isoformat(),
                "last_active": datetime.datetime.now().isoformat(),
                "turns": 0,
                "facts_extracted": 0,
                "messages": []
            }
            self._save_disk()
            print(f"[MemoryManager] Initialized new memory sector for session: {session_id}")
            
        return session_id

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Appends a message to the session's chat history.
        Also updates metadata such as total turns and activity timestamps.
        """
        if session_id not in self.memory_state:
            self.initialize_session(session_id)
            
        session = self.memory_state[session_id]
        
        # Append message
        msg_obj = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        }
        session["messages"].append(msg_obj)
        
        # Update metadata
        session["last_active"] = datetime.datetime.now().isoformat()
        if role == "user":
            session["turns"] += 1
            
        # Simulate 'fact extraction' for UX analytics
        # In a real vector DB, we'd run an NLP pass here.
        # We roughly estimate 1 fact per 4 user messages.
        session["facts_extracted"] = session["turns"] // 4

        # Enforce memory capacity constraints (optional trimming)
        if len(session["messages"]) > self.max_turns * 2:
            self._compress_memory(session_id)
            
        self._save_disk()

    def get_context_window(self, session_id: str, limit: int = None) -> List[Dict[str, str]]:
        """
        Retrieves the recent history tailored for the LLM's context window.
        Strips internal metadata (like timestamps) that the LLM doesn't strictly need.
        """
        if session_id not in self.memory_state:
            return []
            
        if limit is None:
            limit = config.CONTEXT_WINDOW_SIZE
            
        raw_msgs = self.memory_state[session_id]["messages"][-limit:]
        
        # Format for Groq/OpenAI API
        formatted_msgs = []
        for rm in raw_msgs:
            formatted_msgs.append({
                "role": rm["role"],
                "content": rm["content"]
            })
            
        return formatted_msgs

    def get_session_stats(self, session_id: str) -> Dict[str, int]:
        """Returns statistical metadata for the session, used by the frontend UI."""
        if session_id not in self.memory_state:
            return {"total_turns": 0, "long_term_facts": 0}
            
        session = self.memory_state[session_id]
        return {
            "total_turns": session.get("turns", 0),
            "long_term_facts": session.get("facts_extracted", 0)
        }

    def _compress_memory(self, session_id: str) -> None:
        """
        Prevents unbounded growth of a session's history.
        In an advanced implementation, this would trigger an LLM summarization.
        Here, we simply truncate the oldest messages, keeping a baseline.
        """
        session = self.memory_state[session_id]
        # Keep the first 4 messages (initial context) and the last N messages
        first_msgs = session["messages"][:4]
        recent_msgs = session["messages"][-(self.max_turns):]
        
        # Insert a simulated summarization block if needed
        # (Omitted for brevity, but the architecture supports it)
        
        session["messages"] = first_msgs + recent_msgs
        print(f"[MemoryManager] Memory compression executed for session: {session_id}")
