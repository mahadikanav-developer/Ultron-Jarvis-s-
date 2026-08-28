import json
import re
from pathlib import Path


class KnowledgeDatabase:
    """
    ULTRON KNOWLEDGE DATABASE v1

    Responsibilities:
        1. Load knowledge from JSON files.
        2. Normalize user questions.
        3. Match exact questions.
        4. Match aliases.
        5. Select response length.
        6. Return structured knowledge.
        7. Provide database statistics.

    The Knowledge Database does NOT:
        - generate answers
        - browse the internet
        - verify complex answers
        - decide routing

    Those responsibilities belong to other ULTRON components.
    """

    # ================================================================
    # INITIALIZATION
    # ================================================================

    def __init__(self, knowledge_dir=None):

        if knowledge_dir is None:
            knowledge_dir = Path(__file__).resolve().parent

        self.knowledge_dir = Path(knowledge_dir)

        self.entries = []
        self.exact_index = {}
        self.alias_index = {}

        self.load_database()

    # ================================================================
    # NORMALIZATION
    # ================================================================

    @staticmethod
    def normalize(text):
        """
        Normalize a question for reliable matching.

        Examples:

            What is Gravity?
            what   is   gravity!!!
            WHAT IS GRAVITY?

        become:

            what is gravity
        """

        if text is None:
            return ""

        text = str(text).lower().strip()

        # Normalize smart quotes.
        text = (
            text.replace("“", '"')
                .replace("”", '"')
                .replace("‘", "'")
                .replace("’", "'")
        )

        # Remove punctuation but preserve useful technical symbols.
        text = re.sub(
            r"[^a-z0-9+#./_+\- ]",
            " ",
            text,
        )

        # Collapse whitespace.
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ================================================================
    # DATABASE LOADING
    # ================================================================

    def load_database(self):
        """
        Load every JSON knowledge file in the knowledge directory.
        """

        self.entries.clear()
        self.exact_index.clear()
        self.alias_index.clear()

        json_files = sorted(
            self.knowledge_dir.glob("*.json")
        )

        for file_path in json_files:

            try:
                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                ) as file:

                    data = json.load(file)

            except (OSError, json.JSONDecodeError) as error:

                print(
                    f"[KNOWLEDGE] Failed to load "
                    f"{file_path.name}: {error}"
                )

                continue

            if not isinstance(data, list):

                print(
                    f"[KNOWLEDGE] Skipping "
                    f"{file_path.name}: expected a list."
                )

                continue

            for entry in data:

                if not isinstance(entry, dict):
                    continue

                self.add_entry(
                    entry,
                    source=file_path.name,
                )

    # ================================================================
    # ADD ENTRY
    # ================================================================

    def add_entry(self, entry, source=None):
        """
        Add one knowledge entry to memory.

        Expected structure:

        {
            "id": "...",
            "aliases": [...],
            "category": "...",
            "answers": {
                "short": "...",
                "normal": "...",
                "detailed": "..."
            }
        }
        """

        entry_id = entry.get("id")

        if not entry_id:
            return False

        aliases = entry.get("aliases", [])

        if not isinstance(aliases, list):
            aliases = []

        answers = entry.get("answers", {})

        if not isinstance(answers, dict):
            answers = {}

        category = entry.get(
            "category",
            "general",
        )

        normalized_aliases = []

        for alias in aliases:

            normalized = self.normalize(alias)

            if normalized:
                normalized_aliases.append(normalized)

        # Add ID as a searchable term.
        normalized_id = self.normalize(entry_id)

        if normalized_id:
            normalized_aliases.append(normalized_id)

        stored_entry = {
            "id": entry_id,
            "category": category,
            "aliases": normalized_aliases,
            "answers": {
                "short": answers.get("short", ""),
                "normal": answers.get("normal", ""),
                "detailed": answers.get("detailed", ""),
            },
            "source": source,
        }

        self.entries.append(stored_entry)

        # Build indexes.
        for alias in normalized_aliases:

            if alias not in self.alias_index:
                self.alias_index[alias] = stored_entry

        # Direct ID lookup.
        if normalized_id:
            self.exact_index[
                normalized_id
            ] = stored_entry

        return True

    # ================================================================
    # SEARCH
    # ================================================================

    def search(
        self,
        query,
        mode="short",
        category=None,
    ):
        """
        Search the knowledge database.

        Returns:

            structured result

        or:

            None
        """

        normalized_query = self.normalize(query)

        if not normalized_query:
            return None

        # ------------------------------------------------------------
        # Exact alias match
        # ------------------------------------------------------------

        entry = self.alias_index.get(
            normalized_query
        )

        if entry is not None:

            if (
                category is not None
                and entry["category"] != category
            ):
                return None

            return self._format_result(
                entry,
                mode,
                match_type="exact",
                query=query,
            )

        # ------------------------------------------------------------
        # Lightweight matching
        # ------------------------------------------------------------

        best_entry = None
        best_score = 0

        query_words = set(
            normalized_query.split()
        )

        for candidate in self.entries:

            if (
                category is not None
                and candidate["category"] != category
            ):
                continue

            for alias in candidate["aliases"]:

                alias_words = set(
                    alias.split()
                )

                if not alias_words:
                    continue

                overlap = len(
                    query_words & alias_words
                )

                if overlap == 0:
                    continue

                # Jaccard-like score.
                union = len(
                    query_words | alias_words
                )

                score = overlap / union

                # Exact word containment gets a bonus.
                if (
                    normalized_query in alias
                    or alias in normalized_query
                ):
                    score += 0.35

                if score > best_score:

                    best_score = score
                    best_entry = candidate

        # Require a reasonably strong match.
        if best_entry is not None and best_score >= 0.60:

            return self._format_result(
                best_entry,
                mode,
                match_type="semantic_light",
                query=query,
                score=round(best_score, 2),
            )

        return None

    # ================================================================
    # RESULT FORMAT
    # ================================================================

    def _format_result(
        self,
        entry,
        mode,
        match_type,
        query,
        score=None,
    ):
        """
        Create a predictable result object.
        """

        if mode not in {
            "short",
            "normal",
            "detailed",
        }:
            mode = "short"

        answer = entry["answers"].get(
            mode,
            "",
        )

        # Fallback if requested mode doesn't exist.
        if not answer:

            for fallback_mode in (
                "normal",
                "short",
                "detailed",
            ):

                answer = entry["answers"].get(
                    fallback_mode,
                    "",
                )

                if answer:
                    break

        result = {
            "found": bool(answer),
            "answer": answer,
            "id": entry["id"],
            "category": entry["category"],
            "match_type": match_type,
            "source": entry["source"],
            "query": query,
        }

        if score is not None:
            result["score"] = score

        return result

    # ================================================================
    # STATISTICS
    # ================================================================

    def stats(self):
        """
        Return database statistics.
        """

        categories = {}

        for entry in self.entries:

            category = entry["category"]

            categories[category] = (
                categories.get(category, 0) + 1
            )

        return {
            "entries": len(self.entries),
            "search_terms": len(
                self.alias_index
            ),
            "categories": categories,
            "files": len(
                list(
                    self.knowledge_dir.glob("*.json")
                )
            ),
        }

    # ================================================================
    # RELOAD
    # ================================================================

    def reload(self):
        """
        Reload JSON knowledge from disk.
        """

        self.load_database()