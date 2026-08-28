try:
    import wikipedia
except ImportError:
    wikipedia = None

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

class Research:
    """
    ULTRON COMPREHENSIVE RESEARCH ENGINE
    """

    def __init__(self):
        self.ddgs = DDGS() if DDGS else None
        if wikipedia:
            try:
                wikipedia.set_lang("en")
            except Exception:
                pass

    def search_reddit(self, query, max_posts=3):
        """Searches Reddit discussions safely using DDGS site filter."""
        if not self.ddgs:
            print("[RESEARCH ERROR] Missing dependency: ddgs")
            return ""

        clean_q = query.lower().replace("reddit", "").strip()
        reddit_query = f"{clean_q} site:reddit.com"
        
        try:
            results = list(self.ddgs.text(reddit_query, backend="html", max_results=max_posts))
            if not results:
                return ""

            context = "--- Reddit / Community Discussions ---\n"
            for res in results:
                title = res.get("title", "").replace(" : r/", " - r/").replace(" - Reddit", "")
                body = res.get("body", "")
                context += f"Post: {title}\nDiscussion: {body}\n\n"
            return context
        except Exception as e:
            print(f"[RESEARCH ERROR] Reddit search failed: {e}")
            return ""

    def search_wikipedia(self, query):
        if not wikipedia:
            print("[RESEARCH ERROR] Missing dependency: wikipedia")
            return ""

        try:
            clean_q = query.lower()
            for prefix in ["what is ", "who is ", "define ", "tell me about "]:
                if clean_q.startswith(prefix):
                    clean_q = clean_q[len(prefix):]
            summary = wikipedia.summary(clean_q.strip(), sentences=3, auto_suggest=False)
            return f"--- Encyclopedia Summary ---\n{summary}\n\n"
        except Exception:
            return ""

    def search_web(self, query, max_results=3):
        if not self.ddgs:
            print("[RESEARCH ERROR] Missing dependency: ddgs")
            return ""

        try:
            results = list(self.ddgs.text(query, backend="html", max_results=max_results))
            if not results:
                return ""
            context = "--- Live Web Results ---\n"
            for idx, res in enumerate(results):
                title = res.get("title", "Source")
                body = res.get("body", "")
                context += f"[{idx+1}] {title}: {body}\n\n"
            return context
        except Exception as e:
            print(f"[RESEARCH ERROR] Web search failed: {e}")
            return ""

    def run_search(self, query, max_results=3):
        print(f"[RESEARCH] Initiating multi-source scan for: '{query}'...")
        query_lower = query.lower()
        context = ""

        # 1. Definitional check (Wiki)
        wiki_triggers = ["what is ", "who is ", "define ", "tell me about "]
        if any(query_lower.startswith(prefix) for prefix in wiki_triggers):
            context += self.search_wikipedia(query)

        # 2. Reddit discussions for product comparisons, reviews, etc.
        community_triggers = ["best", "review", "worth it", "vs", "recommend", "how to", "issue", "fix", "mouse", "keyboard", "gpu"]
        if any(t in query_lower for t in community_triggers) or "reddit" in query_lower:
            context += self.search_reddit(query, max_posts=3)

        # 3. Always include general web search results
        context += self.search_web(query, max_results=max_results)

        if context.strip():
            print("[RESEARCH] Multi-source context compiled successfully.")
            return f"RESEARCH CONTEXT:\n{context}"
        
        print("[RESEARCH] No results found across any channel.")
        return ""
