import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.core1 import Core1
from core.core2 import Core2
from core.router import Router
from core.runtime import UltronRuntime
from knowledge.database import KnowledgeDatabase
from memory.memory import Memory
from personality.ultron_touch import UltronTouch
from pipeline.pipeline1 import Pipeline1
from pipeline.pipeline15 import Pipeline15
from pipeline.pipeline2 import Pipeline2
from tools.tools import Tools


class MockAIEngine:
    def __init__(self, response="Mock AI response", verification_json=None):
        self.response = response
        self.verification_json = verification_json

    def generate(self, prompt, response_mode="normal", raw=False):
        if "ULTRON CORE 2" in prompt:
            if self.verification_json is not None:
                return self.verification_json
            return '{"approved": true, "confidence": 0.95, "issues": "None", "improved_answer": "Verified response"}'
        return self.response


class OfflineAIEngine:
    def generate(self, prompt, response_mode="normal", raw=False):
        return None


class IntegrationFlowTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_file = os.path.join(self.temp_dir.name, "test_memory.json")
        self.memory = Memory(memory_file=self.memory_file)
        self.tools = Tools()
        self.database = KnowledgeDatabase()
        self.core1 = Core1()
        self.touch = UltronTouch()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_runtime(self, ai_engine):
        core2 = Core2(ai_engine)
        p1 = Pipeline1(tools=self.tools, database=self.database, memory=self.memory)
        p15 = Pipeline15(ai_engine=ai_engine, tools=self.tools, database=self.database, memory=self.memory)
        p2 = Pipeline2(ai_engine=ai_engine, core2=core2, memory=self.memory)
        
        # Mock external search by default to guarantee fast, deterministic, offline integration tests
        p15.research.run_search = lambda q, max_results=3: f"Relevant search facts for {q}"
        p2.research.run_search = lambda q, max_results=4: f"Relevant deep research facts for {q}"
        
        router = Router(pipeline1=p1, pipeline15=p15, pipeline2=p2, tools=self.tools, core2=core2)
        
        runtime = UltronRuntime()
        runtime.core1 = self.core1
        runtime.database = self.database
        runtime.ai = ai_engine
        runtime.core2 = core2
        runtime.tools = self.tools
        runtime.memory = self.memory
        runtime.ultron_touch = self.touch
        runtime.pipeline1 = p1
        runtime.pipeline15 = p15
        runtime.pipeline2 = p2
        runtime.router = router
        return runtime

    def test_flow_simple_db_hit(self):
        """Test: simple known question -> Core1 -> Router -> Pipeline1 -> verified output (0 AI tokens)"""
        runtime = self._create_runtime(MockAIEngine())
        result = runtime.process_turn("hello")

        self.assertIn("operational", result["answer"].lower())
        self.assertEqual(result["route"], "pipeline1")
        self.assertEqual(result["analysis"]["intent"], "greeting")

    def test_flow_db_miss_escalates_to_pipeline15(self):
        """Test: database miss -> Pipeline1 escalates to Pipeline 1.5"""
        ai = MockAIEngine(response="Synthesized answer for topic")
        runtime = self._create_runtime(ai)
        # Mock research to return text that overlaps with query keywords
        runtime.pipeline15.research.run_search = lambda q, max_results=3: "Relevant topic information and facts."
        
        result = runtime.process_turn("Tell me about this topic")
        self.assertEqual(result["route"], "pipeline15")
        self.assertTrue(len(result["answer"]) > 0)

    def test_flow_research_failure_escalates_to_pipeline2(self):
        """Test: low quality/failed research in Pipeline 1.5 -> escalates to Pipeline 2"""
        ai = MockAIEngine(response="Deep reasoning response")
        runtime = self._create_runtime(ai)
        # Mock research to return empty / zero overlap context
        runtime.pipeline15.research.run_search = lambda q, max_results=3: ""
        runtime.pipeline2.research.run_search = lambda q, max_results=4: "Deep reasoning facts."
        
        result = runtime.process_turn("Tell me about this topic")
        self.assertEqual(result["route"], "pipeline2")
        self.assertTrue(len(result["answer"]) > 0)

    def test_flow_specialist_to_pipeline2_and_core2(self):
        """Test: specialist coding request -> Core1 -> Pipeline2 -> Core2 verification"""
        ai = MockAIEngine(
            response="def reverse_tree(root): return root",
            verification_json='{"approved": true, "confidence": 0.98, "issues": "None", "improved_answer": "```python\\ndef reverse_tree(root): return root\\n```"}'
        )
        runtime = self._create_runtime(ai)
        runtime.pipeline2.research.run_search = lambda q, max_results=4: "Binary tree algorithm facts"
        
        result = runtime.process_turn("Write a Python script to reverse a binary tree")
        self.assertEqual(result["analysis"]["intent"], "coding")
        self.assertEqual(result["route"], "pipeline2")
        self.assertIn("def reverse_tree", result["answer"])

    def test_flow_command_to_tools(self):
        """Test: command -> Core1 -> Router -> Tools"""
        runtime = self._create_runtime(MockAIEngine())
        result = runtime.process_turn("lock computer")
        self.assertEqual(result["analysis"]["intent"], "command")
        self.assertEqual(result["route"], "command")
        self.assertTrue("System locked" in result["answer"] or "lock" in result["answer"].lower())

    def test_flow_offline_ollama_fallback(self):
        """Test: offline Ollama -> graceful fallback across pipelines without crashing"""
        runtime = self._create_runtime(OfflineAIEngine())
        runtime.pipeline15.research.run_search = lambda q, max_results=3: "Some valid web research context"
        runtime.pipeline2.research.run_search = lambda q, max_results=4: "Some valid deep research context"
        
        result = runtime.process_turn("Explain a complex cosmological theory in detail")
        self.assertIsNotNone(result["answer"])
        self.assertIn("offline", result["answer"].lower())

    def test_flow_verification_rejection_escalation(self):
        """Test: Pipeline 1.5 draft rejected by Core 2 -> Router escalates to Pipeline 2"""
        calls = {"count": 0}
        class MultiCallAIEngine:
            def generate(self, prompt, response_mode="normal", raw=False):
                if "ULTRON CORE 2" in prompt:
                    calls["count"] += 1
                    if calls["count"] == 1:
                        return '{"approved": false, "confidence": 0.2, "issues": "Hallucination detected", "improved_answer": ""}'
                    return '{"approved": true, "confidence": 0.95, "issues": "None", "improved_answer": "Corrected deep answer"}'
                return "Draft response"

        runtime = self._create_runtime(MultiCallAIEngine())
        runtime.pipeline15.research.run_search = lambda q, max_results=3: "Research query context and details"
        runtime.pipeline2.research.run_search = lambda q, max_results=4: "Research query deep facts"

        analysis = {"route": "pipeline15", "response_mode": "normal", "normalized_input": "Research query"}
        result = runtime.router.route_request("Research query", analysis)
        self.assertEqual(result["route"], "pipeline2")
        self.assertEqual(result["answer"], "Corrected deep answer")

    def test_core2_malformed_json_resilience(self):
        """Test: Core 2 handles malformed JSON, markdown fences, and type irregularities without raising errors"""
        malformed_cases = [
            '```json\n{"approved": "true", "confidence": "0.91", "issues": "None", "improved_answer": "Fixed answer"}\n```',
            'Non-json response from smaller model',
            '{"approved": true, "confidence": "invalid_number", "issues": null, "improved_answer": ""}',
            '{"approved": false, "confidence": 0.1, "issues": "Bad answer"}',
            '',
            None,
        ]

        for case in malformed_cases:
            core2 = Core2(MockAIEngine(verification_json=case))
            res = core2.verify("Test question", "Raw answer")
            self.assertIsInstance(res["approved"], bool)
            self.assertIsInstance(res["confidence"], float)
            self.assertIsInstance(res["issues"], str)
            self.assertIsInstance(res["improved_answer"], str)
            self.assertTrue(len(res["improved_answer"]) > 0)

    def test_ambiguous_queries_deterministic_routing(self):
        """Test: edge case and ambiguous queries produce deterministic routes and outputs"""
        runtime = self._create_runtime(MockAIEngine())
        ambiguous_queries = [
            "",
            "   ",
            "???",
            "!@#$%",
            "12345",
            "a",
            "the",
        ]

        for query in ambiguous_queries:
            result = runtime.process_turn(query)
            self.assertIsInstance(result, dict)
            self.assertIn("answer", result)
            self.assertIn("route", result)


if __name__ == "__main__":
    unittest.main()
