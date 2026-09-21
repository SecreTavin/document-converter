"""Conversão de imagens entre formatos (JPG, PNG, WEBP, BMP, etc.)."""
from pathlib import Path

from PIL import Image


def convert_image(input_path: str, output_path: str) -> str:
    """Converte uma imagem para o formato indicado pela extensão de `output_path`."""
    image = Image.open(input_path)
    target_format = Path(output_path).suffix.lstrip(".").upper()
    if target_format == "JPG":
        target_format = "JPEG"
    if target_format == "JPEG" and image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(output_path, format=target_format)
    return output_path
