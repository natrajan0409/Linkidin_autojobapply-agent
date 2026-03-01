import pypdf
import os
from docx import Document

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def get_resume_content(file_path):
    """Helper to get content regardless of format."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please use PDF or DOCX.")
