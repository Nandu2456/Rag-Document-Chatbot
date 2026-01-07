from groq import Groq
import os
import dotenv
import json
import time
import re

dotenv.load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an intelligent assistant answering questions using provided document sources.

CRITICAL RULES:
1. Answer ONLY based on the provided sources.
2. Reference sources using [1], [2], [3], etc. format when citing information.
3. If you use information from a source, reference it immediately like: "This feature [1] allows you to..."
4. Do NOT use any external knowledge or information not in the provided sources.
5. If the answer is not found in the sources, say: "This information is not available in the provided documents."

Guidelines:
- Be clear, structured, and user-friendly.
- Use citations [1], [2], etc. to reference the source files listed above.
- If the answer comes from multiple sources, cite all of them.
- Provide headings and bullet points where helpful.
"""

def extract_sources_from_answer(answer: str) -> tuple[str, list[dict]]:
    """Extract sources from the answer text and return cleaned answer + sources list"""
    # Look for "Sources: filename1, filename2" pattern at the end
    sources_pattern = r'Sources?:\s*([^\n]+)'
    match = re.search(sources_pattern, answer, re.IGNORECASE)
    
    sources = []
    cleaned_answer = answer
    
    if match:
        sources_text = match.group(1)
        # Split by comma and clean up filenames
        source_files = [s.strip() for s in sources_text.split(',')]
        sources = [{"source": s} for s in source_files if s]
        
        # Remove the sources line from the answer
        cleaned_answer = re.sub(sources_pattern, '', answer, flags=re.IGNORECASE).strip()
    
    return cleaned_answer, sources

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


def generate_answer_stream_with_citations(question: str, contexts: list[str], sources: list[dict] = None):
    """Stream the model answer then emit only the cited sources parsed from metadata labels.

    The generator yields SSE chunks with `text` during the answer stream and a final
    `citations` payload containing only the sources the model referenced (e.g. [1], [2]).
    """
    if sources is None:
        sources = []

    # Build unique (file,page) keys preserving order
    unique_keys = []
    seen = set()
    for md in sources:
        source_name = md.get("source") or md.get("file_name") or "Unknown"
        page = md.get("page")
        key = (source_name, page)
        if key not in seen:
            seen.add(key)
            unique_keys.append(key)

    # Map keys to labels and prepare formatted context for the prompt
    source_labels = {key: f"[{i}]" for i, key in enumerate(unique_keys, start=1)}
    formatted_context = ""
    for chunk, md in zip(contexts, sources):
        source_name = md.get("source") or md.get("file_name") or "Unknown"
        page = md.get("page")
        key = (source_name, page)
        label = source_labels.get(key, "[?]")
        page_display = f", page {page}" if page is not None else ""
        formatted_context += f"\n{label} ({source_name}{page_display}):\n{chunk}\n"

    sources_reference = "\nAvailable Sources:\n"
    for i, (source_name, page) in enumerate(unique_keys, start=1):
        page_display = f" – page {page}" if page is not None else ""
        sources_reference += f"[{i}] {source_name}{page_display}\n"

    # Call model (non-streaming) and stream characters to client
    completion = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct-0905",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Use the following sources to answer the question.
Reference sources using [1], [2], etc. Format.

{sources_reference}

Context from sources:
{formatted_context}

Question: {question}

Please provide a clear explanation with headings or bullet points where helpful. Reference sources using [1], [2], etc."""}
        ],
        temperature=0,
        stream=False
    )

    full_answer = completion.choices[0].message.content

    # Stream text
    for char in full_answer:
        yield f"data: {json.dumps({'text': char})}\n\n"
        time.sleep(0.01)

    # Parse numeric citations the model actually used (e.g. [1], [2])
    cited_indices = set()
    for m in re.finditer(r"\[(\d+)\]", full_answer):
        try:
            cited_indices.add(int(m.group(1)))
        except ValueError:
            continue

    # Build ordered unique source list as dicts
    indexed_unique = []
    seen_keys = set()
    for source_name, page in unique_keys:
        if (source_name, page) not in seen_keys:
            seen_keys.add((source_name, page))
            indexed_unique.append({"source": source_name, "page": page})

    # Select only those cited by the model (1-based indices)
    cited_sources = []
    for idx, entry in enumerate(indexed_unique, start=1):
        if idx in cited_indices:
            cited_sources.append(entry)

    yield f"data: {json.dumps({'citations': cited_sources})}\n\n"


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
    # Deduplicate by (source, page)
    unique = {}
    for md in sources:
        source_name = md.get("source") or md.get("file_name") or "Unknown"
        page = md.get("page")
        key = (source_name, page)
        if key not in unique:
            unique[key] = {"source": source_name, "page": page}

    unique_sources = list(unique.values())

    return {
        "answer": answer,
        "citations": unique_sources
    }
