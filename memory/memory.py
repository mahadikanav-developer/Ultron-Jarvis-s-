import json
from pathlib import Path
from config.settings import MEMORY_FILE, MAX_MEMORY_TURNS

class Memory:
    """
    ULTRON PROPRIETARY MEMORY SYSTEM

    Responsible for:
    - Persistent conversation logging on disk
    - Short-term context window management
    - Supplying historical context to the AI engine for continuity
    """

    def __init__(self, memory_file=MEMORY_FILE):
        self.memory_file = Path(memory_file)
        self.context = []
        self._load_memory()

    def _load_memory(self):
        """Loads persistent memory from disk safely."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.context = data
            except (json.JSONDecodeError, IOError):
                self.context = []
        else:
            self.context = []

    def _save_memory(self):
        """Saves current memory state to disk."""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.context, f, indent=4)
        except IOError as e:
            print(f"[MEMORY ERROR] Could not save context: {e}")

    def add_context(self, user_input, ai_response):
        """Adds a conversation turn to persistent memory."""
        self.context.append({"user": user_input, "assistant": ai_response})
        
        # Keep only the configured interactions to prevent context window bloat
        if len(self.context) > MAX_MEMORY_TURNS:
            self.context.pop(0)
            
        self._save_memory()

    def get_context_string(self):
        """Formats memory into a block readable by the AI Engine."""
        if not self.context:
            return ""
        
        history = "RECENT CONVERSATION HISTORY:\n"
        for turn in self.context[-5:]:  # Pull the last 5 turns for immediate context
            user_msg = turn.get("user", "")
            assistant_msg = turn.get("assistant", turn.get("ultron", ""))
            history += f"User: {user_msg}\nAssistant: {assistant_msg}\n"
        return history