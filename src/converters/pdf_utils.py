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


class WrongPasswordError(RuntimeError):
    """Levantado quando a senha informada não abre o PDF."""


def add_password(pdf_path: str, password: str, output_path: str) -> str:
    """Protege um PDF com senha (necessária para abri-lo depois)."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    writer.append(reader)
    writer.encrypt(password)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def remove_password(pdf_path: str, password: str, output_path: str) -> str:
    """Remove a senha de um PDF protegido, a partir da senha atual."""
    reader = PdfReader(pdf_path)
    if reader.is_encrypted:
        if not reader.decrypt(password):
            raise WrongPasswordError("Senha incorreta.")
    writer = PdfWriter()
    writer.append(reader)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def rotate_pages(pdf_path: str, output_path: str, rotation: int) -> str:
    """Rotaciona todas as páginas de um PDF em `rotation` graus (90, 180 ou 270)."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(rotation)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def add_watermark(pdf_path: str, output_path: str, text: str, opacity: float = 0.3) -> str:
    """Adiciona uma marca d'água de texto, diagonal, em todas as páginas de um PDF."""
    doc = fitz.open(pdf_path)
    try:
        for page in doc:
            rect = page.rect
            fontsize = max(24, int(min(rect.width, rect.height) / 10))
            point = fitz.Point(rect.width / 4, rect.height / 2)
            page.insert_text(
                point,
                text,
                fontsize=fontsize,
                color=(0.5, 0.5, 0.5),
                fill_opacity=opacity,
                overlay=True,
                morph=(point, fitz.Matrix(45)),
            )
        doc.save(output_path)
    finally:
        doc.close()
    return output_path
