import gradio as gr

from src.query import ask


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""

    try:
        result = ask(question)

        sources_text = ""
        for source in result["sources"]:
            sources_text += (
                f"• {source['title']}\n"
                f"  File: {source['file']}\n"
                f"  Distance: {source['distance']}\n"
                f"  URL: {source['url']}\n\n"
            )

        return result["answer"], sources_text.strip()

    except Exception as error:
        return f"Error: {error}", ""


with gr.Blocks(title="The Unofficial Livingstone Guide") as demo:
    gr.Markdown("# The Unofficial Livingstone Guide")
    gr.Markdown(
        "Ask a question about Livingstone College student life, dining, housing, professors, or campus resources. "
        "Answers are generated only from the retrieved project documents."
    )

    question = gr.Textbox(
        label="Your question",
        placeholder="Example: What do students say are the main strengths of Livingstone College?",
        lines=2,
    )

    ask_button = gr.Button("Ask")

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=8)

    ask_button.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()