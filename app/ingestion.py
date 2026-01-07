from pypdf import PdfReader
from docx import Document

def extract_text(file_path: str, file_type: str) -> list:
    """
    Return a list of page-level texts for the given file.

    - For PDFs: returns a list where each item is the text for that page (page numbers are 1-indexed).
    - For docx/txt/md: returns a single-item list containing the full document text.
    """
    if file_type == "pdf":
        reader = PdfReader(file_path)
        return [page.extract_text() or "" for page in reader.pages]

    elif file_type == "docx":
        doc = Document(file_path)
        full_text = "\n".join([p.text for p in doc.paragraphs])
        return [full_text]

    elif file_type in ["txt", "md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return [f.read()]

    else:
        raise ValueError("Unsupported file format")
