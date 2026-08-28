import json
import re

class Core2:
    """
    ULTRON CORE 2 (The Verification Gatekeeper)
    
    Responsible for checking AI-generated answers for accuracy, 
    hallucinations, and completeness before they are sent to the user.
    """

    def __init__(self, ai_engine):
        self.ai_engine = ai_engine

    def verify(self, user_input, raw_answer):
        """
        Evaluates the raw answer against the user's input.
        Returns a dict with approval status, confidence, and an improved answer.
        """
        
        verification_prompt = f"""
        You are ULTRON CORE 2, an internal strict verification gatekeeper.
        Your job is to review the following User Request and the generated Raw Answer.
        
        USER REQUEST: {user_input}
        RAW ANSWER: {raw_answer}
        
        Task:
        1. Check for factual accuracy and logic.
        2. Check for hallucinations (did the AI make things up?).
        3. If the answer is good, approve it. If it has minor flaws, fix them in the 'improved_answer'.
        
        You MUST respond ONLY with a valid JSON object. Do not include markdown formatting or extra text.
        Schema:
        {{
            "approved": true or false,
            "confidence": 0.0 to 1.0,
            "issues": "Describe any issues, or 'None'",
            "improved_answer": "The finalized, correct answer to show the user."
        }}
        """

        try:
            # We ask the AI engine to verify the answer (Acting as Core 2)
            response = self.ai_engine.generate(verification_prompt, response_mode="short")
            
            # --- SAFETY CHECK FOR OFFLINE ENGINE ---
            if not response:
                print("[CORE 2 WARNING] AI Engine returned None (offline). Bypassing gatekeeper.")
                return {
                    "approved": True,
                    "confidence": 0.5,
                    "issues": "AI Engine offline",
                    "improved_answer": raw_answer if raw_answer else "I couldn't reach the AI engine."
                }
            
            # Robust JSON extraction to handle lighter models that might add markdown (like ```json ... ```)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            
            if json_match:
                verification_data = json.loads(json_match.group(0))
                
                # Ensure the necessary keys exist
                return {
                    "approved": verification_data.get("approved", True),
                    "confidence": verification_data.get("confidence", 0.8),
                    "issues": verification_data.get("issues", "None"),
                    "improved_answer": verification_data.get("improved_answer", raw_answer)
                }
            else:
                # Fallback: If no JSON is found, fail-open so the system doesn't freeze
                print("[CORE 2 WARNING] Failed to parse JSON from verification. Bypassing gatekeeper.")
                return {
                    "approved": True,
                    "confidence": 0.5,
                    "issues": "JSON parsing failure.",
                    "improved_answer": raw_answer
                }

        except Exception as e:
            print(f"[CORE 2 ERROR] Verification system fault: {e}")
            # Fail-open fallback
            return {
                "approved": True,
                "confidence": 0.5,
                "issues": f"System error: {e}",
                "improved_answer": raw_answer if raw_answer else "I couldn't reach the AI engine."
            }