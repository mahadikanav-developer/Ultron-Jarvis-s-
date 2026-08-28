from config.settings import OLLAMA_URL, DEFAULT_MODEL

class AIEngine:

    def __init__(self):
        self.name = "Ollama Cloud"
        self.model = DEFAULT_MODEL
        self.url = OLLAMA_URL

    def generate(self, prompt, response_mode="normal", raw=False):

        if raw:
            final_prompt = prompt
        else:
            if response_mode == "short":
                instruction = """
Answer briefly.
Usually 1-3 sentences.
Give only the information needed to answer the question.
Do not add unnecessary tables, history, sections, or examples.
"""
            elif response_mode == "detailed":
                instruction = """
Give a detailed and well-structured explanation.
Use examples, sections, equations, or tables when they genuinely help.
"""
            else:
                instruction = """
Give a clear, moderately detailed answer.
Be informative without unnecessary length.
"""

            final_prompt = f"""
{instruction}

USER REQUEST:
{prompt}
"""

        payload = {
            "model": self.model,
            "prompt": final_prompt,
            "stream": False,
            "format": "json" if raw else ""  # Tells Ollama to enforce valid JSON mode when raw=True
        }

        try:
            import requests

            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "I couldn't generate a response.")

        except ImportError:
            print("[AI ENGINE CONNECTION ERROR] Missing dependency: requests")
            return None
        except Exception as error:
            print(f"[AI ENGINE CONNECTION ERROR] {error}")
            return None
