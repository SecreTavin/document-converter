"""Utilitários de PDF: juntar, dividir, reordenar e comprimir."""
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter


def merge_pdfs(pdf_paths: List[str], output_path: str) -> str:
    """Junta múltiplos PDFs em um único arquivo, na ordem informada."""
    writer = PdfWriter()
    for path in pdf_paths:
        writer.append(path)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def split_pdf(pdf_path: str, output_dir: str) -> List[str]:
    """Divide um PDF em um arquivo separado para cada página."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stem = Path(pdf_path).stem
    reader = PdfReader(pdf_path)

    output_paths = []
    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = str(Path(output_dir) / f"{stem}_pagina_{i}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        output_paths.append(out_path)
    return output_paths


def reorder_pages(pdf_path: str, new_order: List[int], output_path: str) -> str:
    """Reordena as páginas de um PDF. `new_order` é uma lista de índices (0-based) na nova ordem desejada."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for index in new_order:
        writer.add_page(reader.pages[index])
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def compress_pdf(pdf_path: str, output_path: str) -> str:
    """Comprime um PDF removendo redundâncias e recompactando fluxos internos."""
    doc = fitz.open(pdf_path)
    try:
        doc.save(
            output_path,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
        )
    finally:
        doc.close()
    return output_path
