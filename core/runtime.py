from ai.engine import AIEngine
from core.core1 import Core1
from core.core2 import Core2
from core.router import Router
from knowledge.database import KnowledgeDatabase
from memory.memory import Memory
from personality.ultron_touch import UltronTouch
from pipeline.pipeline1 import Pipeline1
from pipeline.pipeline15 import Pipeline15
from pipeline.pipeline2 import Pipeline2
from tools.tools import Tools


class UltronRuntime:
    """
    Shared ULTRON runtime graph.

    Owns subsystem initialization and one-turn request processing so terminal,
    UI, and tests can all use the same assistant brain.
    """

    def __init__(self):
        self.core1 = Core1()
        self.database = KnowledgeDatabase()
        self.ai = AIEngine()
        self.core2 = Core2(self.ai)
        self.tools = Tools()
        self.memory = Memory()
        self.ultron_touch = UltronTouch(ai_engine=self.ai)

        self.pipeline1 = Pipeline1(
            tools=self.tools,
            database=self.database,
            memory=self.memory,
        )
        self.pipeline15 = Pipeline15(
            ai_engine=self.ai,
            tools=self.tools,
            database=self.database,
            memory=self.memory,
        )
        self.pipeline2 = Pipeline2(
            ai_engine=self.ai,
            core2=self.core2,
            memory=self.memory,
        )

        self.router = Router(
            pipeline1=self.pipeline1,
            pipeline15=self.pipeline15,
            pipeline2=self.pipeline2,
            tools=self.tools,
            core2=self.core2,
        )

    def process_turn(self, user_input):
        if user_input is None:
            user_input = ""

        user_input = str(user_input).strip()

        if not user_input:
            return {
                "answer": "",
                "analysis": None,
                "route": None,
                "saved": False,
            }

        analysis = self.core1.process(user_input)
        router_result = self.router.route_request(user_input, analysis)
        final_answer = router_result.get("answer")

        if not final_answer:
            final_answer = "I could not produce a response."

        if router_result.get("route") == "command":
            polished_answer = final_answer
        else:
            polished_answer = self.ultron_touch.apply_touch(
                final_answer,
                style_request=analysis.get("response_mode", "normal"),
            )

        self.memory.add_context(user_input, polished_answer)

        return {
            "answer": polished_answer,
            "analysis": analysis,
            "route": router_result.get("route"),
            "raw_result": router_result,
            "saved": True,
        }
