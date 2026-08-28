import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from knowledge.database import KnowledgeDatabase
from pipeline.pipeline1 import Pipeline1


def main():

    print("=" * 70)
    print("ULTRON PIPELINE 1 TEST")
    print("=" * 70)

    database = KnowledgeDatabase()

    pipeline = Pipeline1(
        database=database
    )

    tests = [
        "What is gravity?",
        "What is Google Chrome?",
        "What is AI?",
        "What is something unknown?",
    ]

    for question in tests:

        print()
        print("QUERY:", question)

        result = pipeline.process(
            question,
            mode="short"
        )

        print(
            "FOUND:",
            bool(result.get("answer"))
        )

        print(
            "SOURCE:",
            result.get("source")
        )

        print(
            "ESCALATE:",
            result.get("escalate")
        )

        if result.get("reason"):
            print(
                "REASON:",
                result.get("reason")
            )

        if result.get("answer"):
            print(
                "ANSWER:",
                result.get("answer")
            )


if __name__ == "__main__":
    main()
