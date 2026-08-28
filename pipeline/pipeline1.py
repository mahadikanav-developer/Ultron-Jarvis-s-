import json
import os

class Pipeline1:
    """
    ULTRON PIPELINE 1 (The Fast Path)
    
    Strictly for zero-latency local database lookups and hardcoded responses.
    Operates in milliseconds. Bypasses Core 2 verification because data is pre-approved.
    """

    def __init__(self, tools=None, database=None, memory=None):
        self.tools = tools
        self.database = database
        self.memory = memory
        self.local_db = self._load_local_db()

    def _load_local_db(self):
        """Loads the pre-approved local knowledge base."""
        db_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'general.json')
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("[PIPELINE 1 ERROR] Could not load general.json")
            return []

    def process(self, user_input, mode="short"):
        print("[PIPELINE 1] Executing zero-latency local lookup...")

        if self.database:
            result = self.database.search(user_input, mode=mode)
            if result and result.get("found"):
                print(f"[PIPELINE 1] Local DB Hit: '{result.get('id')}'")
                return {
                    "answer": result.get("answer", ""),
                    "source": "pipeline1_knowledge_database",
                    "verification_required": False,
                    "escalate": False,
                    "match_type": result.get("match_type"),
                    "category": result.get("category"),
                    "id": result.get("id"),
                }

        # 3. Instant Miss -> Escalate to Pipeline 1.5 without touching the web
        print("[PIPELINE 1] Local DB miss. Escalating to Pipeline 1.5...")
        return {"escalate": True}
