import re

class UltronTouch:
    """
    ULTRON TOUCH (Personality Post-Processor)
    
    Responsible for:
    - Stripping out third-party model identities and AI disclaimers
    - Enforcing clean, professional formatting
    - Enforcing the ULTRON persona
    """

    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        
        self.ai_disclaimers = [
            r"as an ai language model,?\s*",
            r"as an artificial intelligence,?\s*",
            r"i am an ai,?\s*",
            r"i'm an ai,?\s*",
            r"i am a large language model,?\s*",
            r"i don't have personal opinions,?\s*",
            r"i cannot have feelings,?\s*",
            r"please note that i am an ai,?\s*",
            r"i am chatgpt,?\s*",
            r"i'm chatgpt,?\s*",
            r"as chatgpt,?\s*",
        ]

    def apply_touch(self, text, style_request="normal"):
        if not text:
            return "I am unable to generate a response at this time."

        polished_text = text

        # 1. Eradicate generic disclaimers and competitor names
        for disclaimer in self.ai_disclaimers:
            polished_text = re.sub(disclaimer, "", polished_text, flags=re.IGNORECASE)

        # 2. Fix capitalization
        if polished_text and polished_text[0].islower():
            polished_text = polished_text[0].upper() + polished_text[1:]

        # 3. Clean up spacing
        polished_text = polished_text.lstrip(", ").strip()

        if style_request == "short":
            polished_text = polished_text.replace("\n\n", "\n")

        return polished_text