from config.settings import MIN_RESEARCH_QUALITY_SCORE

class ResearchQualityFilter:
    """
    ULTRON RESEARCH QUALITY FILTER v1

    Checks whether research is relevant enough to
    be passed to Core 2.
    """

    def __init__(self):
        self.minimum_score = MIN_RESEARCH_QUALITY_SCORE

    def evaluate(self, query, answer):

        if not answer:
            return {
                "acceptable": False,
                "score": 0.0,
                "reason": "empty_answer"
            }

        query_words = self._keywords(query)
        answer_words = self._keywords(answer)

        if not query_words or not answer_words:
            return {
                "acceptable": False,
                "score": 0.0,
                "reason": "insufficient_text"
            }

        overlap = query_words & answer_words

        score = len(overlap) / len(query_words)

        # Give a small bonus when important query terms
        # appear multiple times in the answer.
        if len(overlap) >= 2:
            score += 0.15

        score = min(score, 1.0)

        acceptable = score >= self.minimum_score

        return {
            "acceptable": acceptable,
            "score": round(score, 2),
            "reason": (
                "relevant_research"
                if acceptable
                else "low_relevance"
            )
        }

    def _keywords(self, text):

        stop_words = {
            "what", "what's", "is", "are",
            "the", "a", "an", "how",
            "does", "do", "did", "explain",
            "define", "why", "can", "you",
            "tell", "me", "about", "of",
            "in", "on", "for", "to"
        }

        words = set()

        for word in text.lower().split():

            word = word.strip(
                ".,!?;:()[]{}\"'"
            )

            if (
                word
                and word not in stop_words
                and len(word) > 2
            ):
                words.add(word)

        return words