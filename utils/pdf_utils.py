"""Resume document text extraction helpers."""

from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree

import pypdf


def extract_resume_text(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()
    if extension == ".pdf":
        reader = pypdf.PdfReader(file_path)
        return " ".join(page.extract_text() or "" for page in reader.pages)

    if extension == ".docx":
        with ZipFile(file_path) as document:
            xml = document.read("word/document.xml")
        root = ElementTree.fromstring(xml)
        namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        return " ".join(node.text for node in root.iter(f"{namespace}t") if node.text)

    raise ValueError("Only PDF and DOCX resumes are supported")
