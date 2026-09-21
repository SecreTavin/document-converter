"""Conversões entre imagens (JPG/PNG/etc.) e PDF."""
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from PIL import Image


def images_to_pdf(image_paths: List[str], output_path: str) -> str:
    """Junta uma ou mais imagens em um único PDF, uma imagem por página."""
    images = [Image.open(p).convert("RGB") for p in image_paths]
    first, rest = images[0], images[1:]
    first.save(output_path, save_all=True, append_images=rest)
    return output_path


def pdf_to_images(pdf_path: str, output_dir: str, fmt: str = "png", dpi: int = 200) -> List[str]:
    """Extrai cada página de um PDF como um arquivo de imagem separado."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stem = Path(pdf_path).stem
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    output_paths = []
    doc = fitz.open(pdf_path)
    try:
        for page_number, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=matrix)
            out_path = str(Path(output_dir) / f"{stem}_pagina_{page_number}.{fmt}")
            pix.save(out_path)
            output_paths.append(out_path)
    finally:
        doc.close()
    return output_paths
