"""Conversões entre PDF e formatos do Office (Word/Excel/PowerPoint)."""
import shutil
import subprocess
from pathlib import Path

from pdf2docx import Converter


class LibreOfficeNotFoundError(RuntimeError):
    """Levantado quando o LibreOffice não está instalado no sistema."""


def _find_soffice() -> str:
    """Localiza o executável do LibreOffice (soffice) no sistema operacional."""
    candidates = [
        "soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for candidate in candidates:
        found = shutil.which(candidate) or (candidate if Path(candidate).exists() else None)
        if found:
            return found
    raise LibreOfficeNotFoundError(
        "LibreOffice não encontrado. Instale o LibreOffice (gratuito) para "
        "converter arquivos do Office para PDF: https://www.libreoffice.org/download/"
    )


def pdf_to_docx(pdf_path: str, output_path: str) -> str:
    """Converte um PDF em um documento Word (.docx), preservando layout, sem depender de programas externos."""
    cv = Converter(pdf_path)
    try:
        cv.convert(output_path)
    finally:
        cv.close()
    return output_path


def office_to_pdf(input_path: str, output_dir: str) -> str:
    """Converte .docx/.xlsx/.pptx para PDF usando o LibreOffice em modo headless."""
    soffice = _find_soffice()
    subprocess.run(
        [
            soffice,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path,
        ],
        check=True,
        capture_output=True,
    )
    stem = Path(input_path).stem
    return str(Path(output_dir) / f"{stem}.pdf")
