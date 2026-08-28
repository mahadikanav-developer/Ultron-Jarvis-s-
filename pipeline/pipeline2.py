from pipeline.research import Research
from pipeline.research_quality import ResearchQualityFilter

class Pipeline2:
    """
    ULTRON Pipeline 2

    Slow/intelligent path.
    """

    def __init__(self, ai_engine, core2, memory=None):
        self.ai_engine = ai_engine
        self.core2 = core2
        self.memory = memory
        self.research = Research() # Give Pipeline 2 its own research capability
        self.quality_filter = ResearchQualityFilter()

    def process(self, user_input, response_mode="normal"):

        print()
        print("[PIPELINE 2]")
        print("Research / AI reasoning required.")

        # 1. Pipeline 2 does a deeper research pass if escalated
        web_context = self.research.run_search(user_input, max_results=4)

        # 1.5 Evaluate research quality using lexical quality filter
        if web_context:
            quality = self.quality_filter.evaluate(user_input, web_context)
            if not quality.get("acceptable"):
                print(f"[PIPELINE 2] Scraped context failed quality gate (Score: {quality.get('score')}). Proceeding without web context.")
                web_context = ""

        # 2. MEMORY INTEGRATION
        context_string = ""
        if self.memory:
            context_string = self.memory.get_context_string()

        # 3. Combine contexts
        context_blocks = []
        if context_string:
            context_blocks.append(context_string)
        if web_context:
            context_blocks.append(web_context)

        if context_blocks:
            combined_context = "\n\n".join(context_blocks)
            effective_prompt = f"Provide an objective, highly accurate answer based on the facts below:\n\n{combined_context}\n\nCURRENT USER REQUEST:\n{user_input}"
        else:
            effective_prompt = user_input

        # 4. AI GENERATION
        ai_response = self.ai_engine.generate(effective_prompt, response_mode)

        if not ai_response:
            print("[PIPELINE 2] AI Engine offline or returned empty response.")
            return {
                "answer": "I am currently offline and cannot process deep reasoning queries.",
                "source": "pipeline2_offline_fallback",
                "verification_required": False,
                "verified": False,
                "confidence": 0.0,
                "fallback": True
            }

        # 5. CORE 2 VERIFICATION
        print()
        print("[CORE 2] Verifying answer...")

        verification = self.core2.verify(user_input, ai_response)

        print("Approved:", verification.get("approved"))
        print("Confidence:", verification.get("confidence"))
        if verification.get("issues"):
            print("Issues:", verification.get("issues"))

        # 6. FINAL PIPELINE RESULT
        if verification.get("approved"):
            return {
                "answer": verification.get("improved_answer", ai_response),
                "source": "pipeline2",
                "verification_required": True,
                "verified": True,
                "confidence": verification.get("confidence", 0)
            }
            
        # Allow self-correction to pass if Core 2 fixed the issue
        if verification.get("improved_answer") and verification.get("confidence", 0) >= 0.5:
            print("[CORE 2] Applying auto-corrected answer from verification.")
            return {
                "answer": verification.get("improved_answer"),
                "source": "pipeline2_corrected",
                "verification_required": True,
                "verified": True,
                "confidence": verification.get("confidence")
            }

        # 7. FALLBACK
        return {
            "answer": "I couldn't verify a reliable answer.",
            "source": "pipeline2",
            "verification_required": True,
            "verified": False,
            "confidence": 0,
            "fallback": True
        }