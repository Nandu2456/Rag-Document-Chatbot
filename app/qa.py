from groq import Groq
import os
import dotenv
import json
import time

dotenv.load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an intelligent assistant that answers questions using the provided document context.

Rules:
1. Prefer the document context whenever it is relevant.
2. If the context partially answers the question, explain using the available information and clearly mention any missing parts.
3. If the answer is not found in the document, say so politely and tell answer is not provided in the document
4. Be clear, structured, and user-friendly.
"""

def generate_answer_stream(question: str, contexts: list[str], sources: list[dict] = None):
    """Get full answer and stream it character by character for UI effect"""
    context_text = "\n\n".join(contexts)

    # Get the full response (not streaming from API)
    completion = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct-0905",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f""" Context: {context_text} Question: {question}
                Please provide a clear explanation with headings or bullet points where helpful."""}
            
        ],
        temperature=0,
        stream=False
    )

    answer = completion.choices[0].message.content
    
    # Stream character by character to frontend
    for char in answer:
        yield f"data: {json.dumps({'text': char})}\n\n"
        # Small delay for better streaming effect
        time.sleep(0.01)


def generate_answer(question: str, contexts: list[str]) -> str:
    context_text = "\n\n".join(contexts)

    completion = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct-0905",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion:\n{question}"}
        ],
        temperature=0
    )

    return completion.choices[0].message.content


def generate_answer_with_citations(question: str, contexts: list[str], sources: list[dict]) -> dict:
    context_text = "\n\n".join(contexts)

    completion = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct-0905",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion:\n{question}"}
        ],
        temperature=0
    )

    answer = completion.choices[0].message.content

    unique_sources = list(
        {source.get("source"): source for source in sources}.values()
    )

    return {
        "answer": answer,
        "citations": unique_sources
    }
