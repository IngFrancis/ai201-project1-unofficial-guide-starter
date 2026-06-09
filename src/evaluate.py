from pathlib import Path
from query import ask


EVAL_OUTPUT = Path("evaluation_results.md")

TEST_QUESTIONS = [
    {
        "question": "What do students say are the main strengths of Livingstone College?",
        "expected": "Students commonly describe Livingstone as close-knit, supportive, family-like, and full of HBCU pride. Some reviews mention helpful professors, student growth, and opportunities to get involved.",
    },
    {
        "question": "What are common complaints students mention about Livingstone College?",
        "expected": "Common complaints include organization issues, housing or dorm concerns, dining variety, communication problems, transportation, and outdated facilities.",
    },
    {
        "question": "What should a new student know before coming to Livingstone?",
        "expected": "Students should stay organized, follow up with offices like financial aid or housing, keep copies of important documents, get involved socially, and be prepared to advocate for themselves.",
    },
    {
        "question": "What dining or meal plan information is available for Livingstone students?",
        "expected": "The dining source mentions meal plan options, commuter plans, dining hall use, bonus points, and rules about unused meals and refunds.",
    },
    {
        "question": "What scholarships does Livingstone offer for computer science students?",
        "expected": "The collected documents do not contain enough information about computer science scholarships, so the system should say it does not have enough information.",
    },
]


def format_sources(sources):
    lines = []
    for source in sources:
        lines.append(
            f"- {source['title']} | File: {source['file']} | Distance: {source['distance']} | URL: {source['url']}"
        )
    return "\n".join(lines)


def main():
    report = ["# Evaluation Results\n"]

    for i, item in enumerate(TEST_QUESTIONS, start=1):
        question = item["question"]
        expected = item["expected"]

        print("=" * 100)
        print(f"Question {i}: {question}")

        result = ask(question)
        answer = result["answer"]
        sources = result["sources"]

        report.append(f"## Question {i}\n")
        report.append(f"**Question:** {question}\n")
        report.append(f"**Expected answer:** {expected}\n")
        report.append(f"**System answer:**\n\n{answer}\n")
        report.append("**Retrieved sources:**\n")
        report.append(format_sources(sources) + "\n")
        report.append("**Accuracy judgment:** TODO: Accurate / Partially accurate / Inaccurate\n")
        report.append("**Notes:** TODO\n")
        report.append("\n---\n")

        print(answer)
        print("\nSources:")
        print(format_sources(sources))
        print()

    EVAL_OUTPUT.write_text("\n".join(report), encoding="utf-8")
    print(f"\nSaved evaluation report to {EVAL_OUTPUT}")


if __name__ == "__main__":
    main()