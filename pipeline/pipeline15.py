from pipeline.research import Research
from pipeline.research_quality import ResearchQualityFilter

class Pipeline15:
    """
    ULTRON PIPELINE 1.5 (Live Research Path)
    """

    def __init__(self, ai_engine, tools=None, database=None, memory=None):
        self.ai_engine = ai_engine
        self.tools = tools
        self.database = database
        self.memory = memory
        self.research = Research()
        self.quality_filter = ResearchQualityFilter()

    def _resolve_context_query(self, user_input):
        """Replaces ambiguous pronouns with active conversation context if present."""
        pronouns = {" it", " this", " that", " them", " it?", " this?", " that?", " them?"}
        query_lower = user_input.lower()
        
        # If the query contains vague pronouns and we have prior context in memory
        if any(p in query_lower for p in pronouns) and self.memory and self.memory.context:
            last_turn = self.memory.context[-1]
            last_query = last_turn.get("user", "")
            # Combine prior query keywords with current question for the search engine
            return f"{user_input} (context: {last_query})"
        return user_input

    def process(self, user_input, mode="normal"):
        # 1. Resolve ambiguous pronouns using conversation memory
        search_query = self._resolve_context_query(user_input)
        
        # 2. Fetch live multi-source research
        web_context = self.research.run_search(search_query, max_results=3)
        
        if not web_context:
            print("[PIPELINE 1.5] Web research yielded no usable data. Escalating to Pipeline 2...")
            return {"escalate": True}

        # 2.5 Evaluate research quality using lexical quality filter
        quality = self.quality_filter.evaluate(user_input, web_context)
        if not quality.get("acceptable"):
            print(f"[PIPELINE 1.5] Web research failed quality check (Score: {quality.get('score')}). Escalating to Pipeline 2...")
            return {"escalate": True}

        # 3. Gather conversation history
        context_string = ""
        if self.memory:
            context_string = self.memory.get_context_string()

        # 4. Build strict context prompt
        prompt = f"""You are ULTRON, a precise AI assistant.
Answer the user's request using ONLY the LIVE WEB DATA and CONTEXT provided below. 
DO NOT invent specifications, materials, or claims not found in the context.

{context_string}

{web_context}

CURRENT USER REQUEST:
{user_input}

ACCURATE ANSWER:"""

        print("[PIPELINE 1.5] Synthesizing live web data...")
        ai_response = self.ai_engine.generate(prompt, response_mode=mode)

        if not ai_response:
            print("[PIPELINE 1.5] AI Engine offline or returned empty response. Escalating to Pipeline 2...")
            return {"escalate": True}

        return {
            "answer": ai_response,
            "source": "pipeline15",
            "research_type": "synthesis",
            "verification_required": True,
            "escalate": False
        }
