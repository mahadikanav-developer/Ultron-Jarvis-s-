import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory.memory import Memory
from pipeline.pipeline15 import Pipeline15
from tools.tools import Tools


class FakeAIEngine:
    def generate(self, prompt, response_mode="normal"):
        return "Test response"


class RuntimeContractTests(unittest.TestCase):

    def test_pipeline15_uses_memory_context_attribute(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_file = os.path.join(temp_dir, "memory.json")
            memory = Memory(memory_file=memory_file)
            memory.add_context("What is Python?", "Python is a programming language.")

            pipeline = Pipeline15(ai_engine=FakeAIEngine(), memory=memory)

            resolved = pipeline._resolve_context_query("Explain it")

            self.assertIn("What is Python?", resolved)

    def test_shutdown_command_is_safely_disabled(self):
        tools = Tools()

        result = tools.execute_command("shutdown_system")

        self.assertFalse(result["success"])
        self.assertIn("disabled for safety", result["message"])

    def test_voice_imports_without_winsound(self):
        # Remove voice.voice if already loaded to force re-import
        if 'voice.voice' in sys.modules:
            del sys.modules['voice.voice']
            
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'winsound':
                raise ImportError("Mocked winsound import failure")
            return original_import(name, *args, **kwargs)
            
        builtins.__import__ = mock_import
        try:
            from voice import voice
            self.assertIsNotNone(voice.startup)
        finally:
            builtins.__import__ = original_import

    def test_pipeline15_escalates_on_offline_engine(self):
        class OfflineAIEngine:
            def generate(self, prompt, response_mode="normal"):
                return None
        
        pipeline = Pipeline15(ai_engine=OfflineAIEngine())
        # Mock search_web to return some context so it doesn't fail on empty search results
        pipeline.research.search_web = lambda query, max_results=3: "Some web info"
        result = pipeline.process("What is python?")
        self.assertTrue(result.get("escalate"))

    def test_pipeline15_escalates_on_poor_quality_context(self):
        pipeline = Pipeline15(ai_engine=FakeAIEngine())
        # Mock run_search to return unrelated info so overlap is 0.0
        pipeline.research.run_search = lambda query, max_results=3: "apples oranges bananas grapes"
        result = pipeline.process("what is a cpu?")
        self.assertTrue(result.get("escalate"))

    def test_pipeline2_returns_fallback_on_offline_engine(self):
        class OfflineAIEngine:
            def generate(self, prompt, response_mode="normal"):
                return None
        from core.core2 import Core2
        from pipeline.pipeline2 import Pipeline2
        
        ai = OfflineAIEngine()
        core2 = Core2(ai)
        pipeline = Pipeline2(ai_engine=ai, core2=core2)
        result = pipeline.process("What is python?")
        self.assertIn("offline", result.get("answer").lower())
        self.assertTrue(result.get("fallback"))

    def test_pipeline1_resolves_via_database(self):
        from pipeline.pipeline1 import Pipeline1
        from knowledge.database import KnowledgeDatabase
        db = KnowledgeDatabase()
        pipeline = Pipeline1(database=db)
        result = pipeline.process("What is gravity?")
        self.assertIsNotNone(result.get("answer"))
        self.assertFalse(result.get("escalate"))
        self.assertEqual(result.get("source"), "pipeline1_knowledge_database")


if __name__ == "__main__":
    unittest.main()
