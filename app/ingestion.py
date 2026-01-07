from pypdf import PdfReader
from docx import Document

def extract_text(file_path: str, file_type: str) -> str:
    if file_type == "pdf":
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() or "" for page in reader.pages])

    elif file_type == "docx":
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file_type in ["txt", "md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError("Unsupported file format")
