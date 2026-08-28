class Router:
    """
    ULTRON ROUTER

    Converts Core 1's decision into the correct execution path.
    Takes the precise routing decision from Core 1 and hands the data 
    off to the correct Pipeline or Tool seamlessly.
    """

    def __init__(self, pipeline1, pipeline15, pipeline2, tools, core2):
        self.pipeline1 = pipeline1
        self.pipeline15 = pipeline15
        self.pipeline2 = pipeline2
        self.tools = tools
        self.core2 = core2

    def route_request(self, user_input, analysis):
        route = analysis.get("route", "pipeline2")
        response_mode = analysis.get("response_mode", "normal")
        normalized_input = analysis.get("normalized_input", user_input)

        # --------------------------------------------------------
        # 1. COMMAND PATH
        # --------------------------------------------------------
        if route == "command":
            print("\n[FAST PATH]")
            command = analysis.get("command")
            result = self.tools.execute_command(command)
            return {
                "answer": result.get("message", "Command executed."),
                "route": "command"
            }

        # --------------------------------------------------------
        # 2. PIPELINE 1 (Local/Fast)
        # --------------------------------------------------------
        elif route == "pipeline1":
            print("\n[PIPELINE 1]")
            result = self.pipeline1.process(normalized_input, mode=response_mode)
            
            if result.get("escalate"):
                print("[PIPELINE 1] Escalating to Pipeline 1.5...")
                return self._run_pipeline15(user_input, normalized_input, response_mode)
                
            raw_answer = result.get("answer")
            
            if result.get("verification_required"):
                print("\n[CORE 2] Verifying Pipeline 1 web result...")
                verification = self.core2.verify(user_input, raw_answer)
                
                if verification.get("approved"):
                    return {"answer": verification.get("improved_answer", raw_answer), "route": "pipeline1"}
                else:
                    print("[PIPELINE 1] Core 2 rejected answer. Escalating to Pipeline 1.5...")
                    return self._run_pipeline15(user_input, normalized_input, response_mode)
                    
            print("[PIPELINE 1] Verified Local DB Hit.")
            return {"answer": raw_answer, "route": "pipeline1"}

        # --------------------------------------------------------
        # 3. PIPELINE 1.5 (Moderate Research)
        # --------------------------------------------------------
        elif route == "pipeline15":
            return self._run_pipeline15(user_input, normalized_input, response_mode)

        # --------------------------------------------------------
        # 4. PIPELINE 2 (Complex/Reasoning)
        # --------------------------------------------------------
        elif route == "pipeline2":
            return self._run_pipeline2(user_input, response_mode)

        # Safe fallback
        return self._run_pipeline2(user_input, response_mode)

    # --- Helper Execution Methods ---

    def _run_pipeline15(self, user_input, normalized_input, response_mode):
        print("\n[PIPELINE 1.5]")
        result = self.pipeline15.process(normalized_input, mode=response_mode)
        
        if result.get("escalate"):
            print("[PIPELINE 1.5] No acceptable answer. Escalating to Pipeline 2...")
            return self._run_pipeline2(user_input, response_mode)
            
        raw_answer = result.get("answer")
        
        if result.get("verification_required"):
            print("\n[CORE 2] Light verification...")
            verification = self.core2.verify(user_input, raw_answer)
            
            if verification.get("approved"):
                return {"answer": verification.get("improved_answer", raw_answer), "route": "pipeline15"}
            else:
                print("[PIPELINE 1.5] Core 2 rejected answer. Escalating to Pipeline 2...")
                return self._run_pipeline2(user_input, response_mode)
                
        return {"answer": raw_answer, "route": "pipeline15"}

    def _run_pipeline2(self, user_input, response_mode):
        # Pipeline 2 handles AI Generation and Core 2 Verification internally
        result = self.pipeline2.process(user_input, response_mode=response_mode)
        
        if result.get("verified") and not result.get("fallback"):
            return {"answer": result.get("answer"), "route": "pipeline2"}
        else:
            return {"answer": result.get("answer", "I couldn't verify a reliable answer."), "route": "pipeline2"}