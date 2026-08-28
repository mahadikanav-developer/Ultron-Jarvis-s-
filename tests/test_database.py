import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from knowledge.database import KnowledgeDatabase


def main():

    db = KnowledgeDatabase()

    print("=" * 70)
    print("ULTRON KNOWLEDGE DATABASE TEST")
    print("=" * 70)

    print("\nDATABASE STATS:")
    print(db.stats())

    tests = [
        ("What is gravity?", "short"),
        ("Define physics", "short"),
        ("what is Google Chrome?", "normal"),
        ("What is a CPU?", "detailed"),
        ("What is AI?", "short"),
        ("What is the internet?", "normal"),
        ("What is something unknown?", "short"),
    ]

    for question, mode in tests:

        print("\n" + "-" * 70)
        print("QUERY:", question)
        print("MODE:", mode)

        result = db.search(
            question,
            mode=mode,
        )

        if result is None:

            print("FOUND: False")
            print("RESULT: No knowledge found.")

        else:

            print("FOUND:", result["found"])
            print("ID:", result["id"])
            print("CATEGORY:", result["category"])
            print("MATCH:", result["match_type"])

            if "score" in result:
                print("SCORE:", result["score"])

            print("ANSWER:", result["answer"])


if __name__ == "__main__":
    main()
