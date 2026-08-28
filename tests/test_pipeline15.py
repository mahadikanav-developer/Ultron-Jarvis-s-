import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.pipeline15 import Pipeline15


class FakeAIEngine:
    def generate(self, prompt, response_mode="normal"):
        return "Test response"


def main():

    print("=" * 70)
    print("ULTRON PIPELINE 1.5 TEST")
    print("=" * 70)

    pipeline = Pipeline15(ai_engine=FakeAIEngine())

    tests = [
        "How does a CPU work?",
        "Explain quantum computing",
        "What is something unknown?",
    ]

    for question in tests:

        print("\n" + "-" * 70)
        print("QUERY:", question)

        result = pipeline.process(
            question,
            mode="short"
        )

        print("ANSWER:", result.get("answer"))
        print("SOURCE:", result.get("source"))
        print(
            "VERIFICATION REQUIRED:",
            result.get("verification_required")
        )
        print("ESCALATE:", result.get("escalate"))

        if result.get("reason"):
            print("REASON:", result.get("reason"))


if __name__ == "__main__":
    main()
