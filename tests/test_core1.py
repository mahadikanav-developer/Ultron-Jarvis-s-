import os
import sys

# Ensure project root is on sys.path so tests can be run directly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.core1 import Core1


core1 = Core1()

tests = [
    "What is gravity?",
    "Who is Albert Einstein?",
    "Is water wet?",
    "Can computers think?",
    "What is Python?",
    "Explain gravity",
    "Explain gravity briefly",
    "Explain gravity in detail",
    "How does a CPU work?",
    "How does a CPU work and why is it important?",
    "Compare Python and Java",
    "Compare Python and C++ in detail",
    "Review this code",
    "Analyze this program",
    "Analyze this document",
    "Research the latest AI news",
    "Research quantum computing",
    "What are the advantages and disadvantages of AI?",
    "What is AI and how does it work?",
    "Open Notepad",
    "Open Chrome",
    "Open Google Chrome",
    "Open VS Code",
    "Open Calculator",
    "Open File Explorer",
    "open NOTEPAD!!!",
    "What is this?",
    "Help",
    "Hello",
    "yes",
    "why?",
    ".NET vs Python",
    "Python vs C++",
    "Tell me about computers",
    "Explain it to me",
    "Explain this in detail",
]


for text in tests:
    print("=" * 80)
    print("TEST:", text)

    result = core1.process(text)

    print("INTENT:", result["intent"])
    print("COMPLEXITY:", result["complexity"])
    print("MODE:", result["response_mode"])
    print("ROUTE:", result["route"])
    print("CONFIDENCE:", result["confidence"])
    print("REASON:", result["route_reason"])
    print("SIGNALS:", result["signals"])