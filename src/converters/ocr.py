"""OCR para PDFs escaneados: transforma páginas-imagem em PDF pesquisável."""
import io
import shutil

import fitz  # PyMuPDF
import pytesseract
from docx import Document
from PIL import Image
from pypdf import PdfWriter

LANGUAGES = {
    "Português": "por",
    "Inglês": "eng",
    "Espanhol": "spa",
}


class TesseractNotFoundError(RuntimeError):
    """Levantado quando o Tesseract OCR não está instalado no sistema."""


def _ensure_tesseract_available():
    if shutil.which("tesseract"):
        return
    raise TesseractNotFoundError(
        "Tesseract OCR não encontrado. Instale para usar o reconhecimento de texto:\n"
        "macOS: brew install tesseract tesseract-lang\n"
        "Windows: https://github.com/UB-Mannheim/tesseract/wiki"
    )


def has_extractable_text(pdf_path: str, min_chars: int = 20) -> bool:
    """Indica se o PDF já tem uma camada de texto (não é apenas imagem escaneada)."""
    doc = fitz.open(pdf_path)
    try:
        total_chars = sum(len(page.get_text().strip()) for page in doc)
    finally:
        doc.close()
    return total_chars >= min_chars


def ocr_pdf(pdf_path: str, output_path: str, lang: str = "por", dpi: int = 300) -> str:
    """Reconhece o texto de um PDF escaneado e gera um PDF pesquisável equivalente."""
    _ensure_tesseract_available()

    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    writer = PdfWriter()

    doc = fitz.open(pdf_path)
    try:
        for page in doc:
            pix = page.get_pixmap(matrix=matrix)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            page_pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, lang=lang, extension="pdf")
            writer.append(io.BytesIO(page_pdf_bytes))
    finally:
        doc.close()

    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def ocr_pdf_to_docx(pdf_path: str, output_path: str, lang: str = "por", dpi: int = 300) -> str:
    """Reconhece o texto de um PDF escaneado e grava o texto extraído em um documento Word.

    Diferente de `office_pdf.pdf_to_docx`, não reconstrói o layout original (o PDF não tem
    um layout de texto real para reconstruir) — apenas extrai o texto reconhecido, uma
    página por seção do documento.
    """
    _ensure_tesseract_available()

    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    document = Document()

    doc = fitz.open(pdf_path)
    try:
        for page_number, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=matrix)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(image, lang=lang).strip()
            if page_number > 1:
                document.add_page_break()
            for line in text.splitlines() or [""]:
                document.add_paragraph(line)
    finally:
        doc.close()

    document.save(output_path)
    return output_path
