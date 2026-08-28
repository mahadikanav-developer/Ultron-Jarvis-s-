import re

class Core1:
    """
    ULTRON CORE 1

    Fast decision / routing layer.

    Core 1:
        - normalizes input
        - detects dynamic commands (OS agnostic with polite prefix stripping)
        - detects intent (including greetings & casual conversation)
        - detects operation
        - scores complexity
        - detects explicit instructions
        - detects multi-part requests
        - selects a pipeline
        - returns explainable routing information

    Core 1 DOES NOT answer questions. Core 2 is responsible for answer verification.
    """

    # ================================================================
    # INTENT VOCABULARY
    # ================================================================

    GREETING_WORDS = {
        "hi", "hello", "hey", "sup", "greetings", "good morning",
        "good afternoon", "good evening", "how are you", "who are you",
        "what is your name", "thanks", "thank you", "bye", "goodbye",
        "how are you doing", "hows it going", "how's it going",
    }

    CASUAL_WORDS = {
        "what are you doing", "what can you do", "help me",
        "tell me a joke", "nice to meet you",
    }

    CODING_WORDS = {
        "python", "code", "program", "programming", "javascript",
        "typescript", "html", "css", "bug", "debug", "coding",
        "github", "repository", "script", "function", "class",
        "api", "java", "c++", "c#", ".net", "node.js",
        "software", "developer", "development",
    }

    MATH_WORDS = {
        "calculate", "solve", "equation", "math", "mathematics",
        "multiply", "divide", "percentage", "algebra", "geometry",
        "probability", "statistics", "integral", "derivative",
        "theorem", "matrix", "calculus",
    }

    SCIENCE_WORDS = {
        "physics", "chemistry", "biology", "science", "quantum",
        "atom", "molecule", "gravity", "energy", "force",
        "experiment", "relativity", "electron", "proton", "neutron",
        "mechanics", "thermodynamics", "electricity", "magnetism",
    }

    RESEARCH_WORDS = {
        "research", "latest", "analysis", "analyze", "analyse",
        "investigate", "examine", "review", "news", "sources",
        "evidence", "study", "report", "findings",
    }

    # ================================================================
    # OPERATIONS
    # ================================================================

    COMPARISON_PHRASES = {
        "compare": 8, "comparison": 8, "vs": 8, "versus": 8,
        "difference between": 8, "differences between": 8,
        "which is better": 8, "pros and cons": 8,
        "advantages and disadvantages": 8,
        "advantages and disadvantages of": 8,
    }

    EXPLANATION_PHRASES = {
        "explain": 5, "how does": 6, "how do": 6, "how is": 5,
        "why does": 6, "why is": 6, "tell me about": 5, "teach me": 8,
    }

    ANALYSIS_PHRASES = {
        "analyze": 8, "analyse": 8, "review": 8, "investigate": 8,
        "examine": 8, "evaluate": 8, "assess": 8, "critique": 8,
    }

    RESEARCH_OPERATION_PHRASES = {
        "research": 16, "latest": 12, "latest news": 14,
        "find sources": 14, "with sources": 14,
        "according to sources": 14, "deep research": 20,
    }

    # ================================================================
    # COMPLEXITY PHRASES
    # ================================================================

    SIMPLE_PHRASES = {
        "is the": 4, "is a": 4, "is an": 4, "what is": 4, "who is": 4,
        "where is": 4, "when is": 4, "can i": 3, "can you": 3,
        "does": 3, "do you": 3, "yes or no": 5, "true or false": 5,
        "briefly": 6, "brief": 6, "short answer": 6, "in short": 6,
        "just answer": 6,
    }

    MODERATE_PHRASES = {
        "explain": 6, "how": 4, "how does": 7, "how do": 7,
        "how is": 6, "why": 5, "why does": 7, "why is": 7,
        "give an example": 5, "examples": 4, "tell me about": 5,
    }

    COMPLEX_PHRASES = {
        "in detail": 12, "detailed explanation": 12, "deep dive": 12,
        "step by step": 10, "analyze": 8, "analyse": 8, "compare": 8,
        "comparison": 8, "vs": 8, "versus": 8, "difference between": 8,
        "differences between": 8, "which is better": 8, "pros and cons": 8,
        "advantages and disadvantages": 8, "review": 8, "investigate": 8,
        "examine": 8, "evaluate": 8, "assess": 8, "critique": 8,
        "review the code": 10, "review this code": 10,
        "examine the document": 10, "examine this document": 10,
        "analyze the document": 10, "analyze this document": 10,
        "analyze the code": 10, "analyze this code": 10, "teach me": 8,
    }

    RESEARCH_PHRASES = {
        "research": 16, "latest": 12, "latest news": 14,
        "research this": 16, "find sources": 14, "with sources": 14,
        "according to sources": 14, "investigate": 16, "deep research": 20,
    }

    # ================================================================
    # EXPLICIT INSTRUCTIONS
    # ================================================================

    EXPLICIT_DETAIL = {
        "in detail", "detailed explanation", "deep dive",
        "step by step", "teach me",
    }

    EXPLICIT_BRIEF = {
        "briefly", "brief", "short answer", "in short", "just answer",
    }

    COMPLEX_OPERATIONS = {
        "compare", "comparison", "vs", "versus", "difference between",
        "differences between", "which is better", "pros and cons",
        "advantages and disadvantages", "analyze", "analyse",
        "review", "investigate", "examine", "evaluate", "assess",
        "critique", "research",
    }

    # ================================================================
    # MAIN PROCESSOR
    # ================================================================

    def process(self, user_input):
        if user_input is None:
            user_input = ""

        if not isinstance(user_input, str):
            user_input = str(user_input)

        original = user_input
        text = self.normalize(user_input)

        if not text:
            return {
                "original_input": original,
                "normalized_input": "",
                "intent": "unknown",
                "operation": "unknown",
                "complexity": "simple",
                "response_mode": "short",
                "route": "pipeline1",
                "scores": {"simple": 0, "moderate": 0, "complex": 0, "research": 0},
                "signals": ["empty_input"],
                "confidence": 1.0,
                "route_reason": "empty_input",
            }

        # ------------------------------------------------------------
        # DYNAMIC COMMAND DETECTION
        # ------------------------------------------------------------
        command = self.detect_command(text)

        if command:
            return {
                "original_input": original,
                "normalized_input": text,
                "intent": "command",
                "operation": "execute",
                "complexity": "simple",
                "response_mode": "short",
                "route": "command",
                "command": command,
                "scores": {"simple": 0, "moderate": 0, "complex": 0, "research": 0},
                "signals": ["command"],
                "confidence": 1.0,
                "route_reason": "recognized_command",
            }

        tokens = text.split()
        word_count = len(tokens)
        intent = self.detect_intent(text, tokens)
        operation = self.detect_operation(text)

        scores = {"simple": 0, "moderate": 0, "complex": 0, "research": 0}
        signals = []

        self.score_phrases(text, self.SIMPLE_PHRASES, "simple", scores, signals)
        self.score_phrases(text, self.MODERATE_PHRASES, "moderate", scores, signals)
        self.score_phrases(text, self.COMPLEX_PHRASES, "complex", scores, signals)
        self.score_phrases(text, self.RESEARCH_PHRASES, "research", scores, signals)

        self.apply_position_scoring(text, scores, signals)
        self.apply_length_scoring(word_count, scores, signals)

        multipart_count = self.detect_multipart(text)
        if multipart_count:
            scores["moderate"] += multipart_count * 3
            signals.append(f"multi_part:{multipart_count}")

        explicit_detail = self.contains_phrase(text, self.EXPLICIT_DETAIL)
        explicit_brief = self.contains_phrase(text, self.EXPLICIT_BRIEF)
        research_request = self.contains_phrase(text, self.RESEARCH_PHRASES)
        complex_operation = self.contains_phrase(text, self.COMPLEX_OPERATIONS)
        comparison_request = self.contains_phrase(text, self.COMPARISON_PHRASES)

        response_mode = self.choose_response_mode(
            word_count=word_count,
            explicit_detail=explicit_detail,
            explicit_brief=explicit_brief,
            complex_operation=complex_operation,
        )

        route, complexity, reason = self.choose_route(
            word_count=word_count,
            scores=scores,
            explicit_detail=explicit_detail,
            explicit_brief=explicit_brief,
            research_request=research_request,
            complex_operation=complex_operation,
            comparison_request=comparison_request,
            multipart_count=multipart_count,
            intent=intent,
            operation=operation,
        )

        confidence = self.calculate_confidence(
            scores=scores,
            route=route,
            explicit_detail=explicit_detail,
            explicit_brief=explicit_brief,
            research_request=research_request,
            comparison_request=comparison_request,
        )

        signals = self.unique_signals(signals)
        signals.append(f"score_route:{complexity}")

        return {
            "original_input": original,
            "normalized_input": text,
            "intent": intent,
            "operation": operation,
            "complexity": complexity,
            "response_mode": response_mode,
            "route": route,
            "scores": scores,
            "signals": signals,
            "confidence": confidence,
            "route_reason": reason,
        }

    # ================================================================
    # NORMALIZATION
    # ================================================================

    def normalize(self, text):
        if text is None:
            return ""
        text = str(text).lower().strip()
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = re.sub(r"[^a-z0-9+#./_+\-? ]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ================================================================
    # DYNAMIC COMMAND DETECTION
    # ================================================================

    def detect_command(self, text):
        """
        Dynamically detects commands without needing hardcoded lists.
        Strips conversational filler like 'can you', 'please', 'could you'.
        """
        if not text:
            return None
        text = str(text).lower().strip()

        # 1. Strip common conversational filler & polite prefixes
        filler_prefixes = [
            "can you please ", "could you please ", "would you please ",
            "can you ", "could you ", "would you ", "please ",
            "ultron please ", "ultron can you ", "ultron "
        ]
        
        cleaned = text
        for prefix in filler_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break

        # 2. App Launching ("open chrome", "launch notepad", "start calc")
        for action in ["open ", "launch ", "start "]:
            if cleaned.startswith(action):
                app_name = cleaned[len(action):].strip()
                app_name = re.sub(r"\s+(please|for me|app|application)$", "", app_name).strip()
                if app_name:
                    return f"open:{app_name}"

        # 3. Screenshot Commands
        if "screenshot" in cleaned or "screen shot" in cleaned or "capture screen" in cleaned:
            return "screenshot"

        # 4. System Controls
        if cleaned in {"lock screen", "lock computer", "lock pc"}:
            return "lock_system"
            
        if cleaned in {"shut down computer", "turn off computer", "shutdown"}:
            return "shutdown_system"

        return None

    # ================================================================
    # INTENT DETECTION
    # ================================================================

    def detect_intent(self, text, tokens):
        token_set = set(tokens)

        # 1. Check Greetings & Small Talk First
        if text in self.GREETING_WORDS or (token_set & {"hi", "hello", "hey", "sup", "greetings"}):
            return "greeting"

        if text in self.CASUAL_WORDS or self.contains_phrase(text, self.CASUAL_WORDS):
            return "casual"

        # 2. Specialist Domains
        if token_set & self.CODING_WORDS:
            return "coding"
        if token_set & self.MATH_WORDS:
            return "mathematics"
        if token_set & self.SCIENCE_WORDS:
            return "science"
        if token_set & self.RESEARCH_WORDS:
            return "research"

        normalized_tokens = {token.strip(".,!?") for token in tokens}

        if normalized_tokens & self.CODING_WORDS:
            return "coding"
        if normalized_tokens & self.MATH_WORDS:
            return "mathematics"
        if normalized_tokens & self.SCIENCE_WORDS:
            return "science"
        if normalized_tokens & self.RESEARCH_WORDS:
            return "research"

        return "general"

    # ================================================================
    # OPERATION DETECTION
    # ================================================================

    def detect_operation(self, text):
        if self.contains_phrase(text, self.RESEARCH_OPERATION_PHRASES):
            return "research"
        if self.contains_phrase(text, self.COMPARISON_PHRASES):
            return "comparison"
        if self.contains_phrase(text, self.ANALYSIS_PHRASES):
            return "analysis"
        if self.contains_phrase(text, self.EXPLANATION_PHRASES):
            return "explanation"

        if (text.startswith("what ") or text.startswith("who ") or
            text.startswith("where ") or text.startswith("when ") or
            text.startswith("why ") or text.startswith("how ") or
            text.startswith("can ") or text.startswith("is ") or
            text.startswith("are ") or text.startswith("does ") or
            text.startswith("do ")):
            return "question"

        return "unknown"

    # ================================================================
    # PHRASE SCORING
    # ================================================================

    def score_phrases(self, text, phrases, category, scores, signals):
        for phrase, weight in phrases.items():
            if self.contains_phrase(text, {phrase}):
                scores[category] += weight
                signal = f"{category}:{phrase}"
                if signal not in signals:
                    signals.append(signal)

    # ================================================================
    # SAFE PHRASE MATCHING
    # ================================================================

    def contains_phrase(self, text, phrases):
        for phrase in phrases:
            escaped = re.escape(phrase.lower())
            pattern = rf"(?<!\w){escaped}(?!\w)"
            if re.search(pattern, text):
                return True
        return False

    # ================================================================
    # POSITION SCORING
    # ================================================================

    def apply_position_scoring(self, text, scores, signals):
        tokens = text.split()
        if not tokens:
            return
        total = len(tokens)
        for index, token in enumerate(tokens):
            if token in self.COMPLEX_OPERATIONS:
                position = index / max(total - 1, 1)
                if position <= 0.30:
                    scores["complex"] += 2
                    signal = f"position:early:{token}"
                    if signal not in signals:
                        signals.append(signal)
                elif position >= 0.70:
                    scores["complex"] += 1
                    signal = f"position:late:{token}"
                    if signal not in signals:
                        signals.append(signal)

    # ================================================================
    # LENGTH SCORING
    # ================================================================

    def apply_length_scoring(self, word_count, scores, signals):
        if word_count <= 5:
            scores["simple"] += 1
            signals.append("length:very_short")
        elif word_count <= 10:
            scores["simple"] += 1
            signals.append("length:short")
        elif word_count <= 25:
            scores["moderate"] += 2
            signals.append("length:medium")
        else:
            scores["complex"] += 3
            signals.append("length:long")

    # ================================================================
    # MULTI-PART DETECTION
    # ================================================================

    def detect_multipart(self, text):
        count = 0
        connectors = [
            " and how ", " and why ", " and what ", " and compare ",
            " and explain ", " and give ", " and tell ", " then ",
            " also ", " as well as ",
        ]
        padded = f" {text} "
        for connector in connectors:
            if connector in padded:
                count += 1
        if text.count("?") > 1:
            count += text.count("?") - 1
        return min(count, 3)

    # ================================================================
    # RESPONSE MODE
    # ================================================================

    def choose_response_mode(
        self, word_count, explicit_detail, explicit_brief, complex_operation
    ):
        if explicit_brief:
            return "short"
        if explicit_detail or complex_operation:
            return "detailed"
        if word_count <= 10:
            return "short"
        if word_count <= 25:
            return "normal"
        return "detailed"

    # ================================================================
    # ROUTE SELECTION
    # ================================================================

    def choose_route(
        self, word_count, scores, explicit_detail, explicit_brief,
        research_request, complex_operation, comparison_request,
        multipart_count, intent, operation
    ):
        # 0. Greetings & Casual -> Always Pipeline 1 (Fast local database / instant response)
        if intent in {"greeting", "casual"}:
            return ("pipeline1", "simple", "greeting_or_casual_intent")

        # 1. Specialist Domains -> Always route to Pipeline 2 (DeepSeek/Specialist AI)
        if intent in {"coding", "mathematics", "science"}:
            return ("pipeline2", "complex", "specialist_domain")

        # 2. Research
        if research_request or intent == "research":
            return ("pipeline2", "complex", "research_request")

        # 3. Explicit detail / Comparison / Complex Operations
        if explicit_detail:
            return ("pipeline2", "complex", "explicit_detail")
        if comparison_request:
            return ("pipeline2", "complex", "comparison_request")
        if complex_operation:
            return ("pipeline2", "complex", "complex_operation")

        # 4. Explicit brief
        if explicit_brief:
            return ("pipeline1", "simple", "explicit_brief")

        # 5. Multi-part requests
        if multipart_count >= 1:
            return ("pipeline15", "moderate", "multiple_subtasks")

        # 6. Scoring Thresholds
        if scores["complex"] >= 10:
            return ("pipeline2", "complex", "strong_complex_score")
        if scores["moderate"] > scores["simple"] and scores["moderate"] >= 5:
            return ("pipeline15", "moderate", "strong_moderate_score")
        if scores["simple"] >= scores["moderate"] and scores["simple"] >= 4:
            return ("pipeline1", "simple", "strong_simple_score")

        # 7. Fallback based on length
        if word_count <= 8:
            return ("pipeline1", "simple", "short_input_fallback")
        if word_count <= 25:
            return ("pipeline15", "moderate", "medium_input_fallback")

        return ("pipeline2", "complex", "long_input_fallback")

    # ================================================================
    # CONFIDENCE
    # ================================================================

    def calculate_confidence(
        self, scores, route, explicit_detail, explicit_brief,
        research_request, comparison_request
    ):
        if route == "command":
            return 1.0

        if explicit_detail or explicit_brief or research_request or comparison_request:
            return 0.98

        values = [scores["simple"], scores["moderate"], scores["complex"], scores["research"]]
        values.sort(reverse=True)

        highest = values[0]
        second = values[1]

        if highest == 0:
            return 0.50

        margin = highest - second
        confidence = 0.70 + (min(margin, 10) * 0.025)

        return round(min(confidence, 0.95), 2)

    # ================================================================
    # UNIQUE SIGNALS
    # ================================================================

    def unique_signals(self, signals):
        result = []
        for signal in signals:
            if signal not in result:
                result.append(signal)
        return result