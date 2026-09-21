"""Interface gráfica do Conversor de Documentos."""
import traceback
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from converters import image_convert, image_pdf, office_pdf, pdf_utils

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

OFFICE_EXTENSIONS = [("Word/Excel/PowerPoint", "*.docx *.xlsx *.pptx")]
PDF_EXTENSIONS = [("PDF", "*.pdf")]
IMAGE_EXTENSIONS = [("Imagens", "*.jpg *.jpeg *.png *.bmp *.webp")]


class BaseTab(ctk.CTkFrame):
    """Frame base com um rótulo de status compartilhado por todas as abas."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.status_label = None

    def build_status_label(self, row: int):
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.grid(row=row, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0))

    def set_status(self, text: str, is_error: bool = False):
        self.status_label.configure(text=text, text_color="#e53935" if is_error else "#43a047")

    def run_safely(self, action):
        try:
            action()
        except Exception as exc:  # noqa: BLE001 - erro é reportado ao usuário, não silenciado
            self.set_status(f"Erro: {exc}", is_error=True)
            traceback.print_exc()
        else:
            self.set_status("Concluído com sucesso.")


class PdfOfficeTab(BaseTab):
    """PDF -> Word e Word/Excel/PowerPoint -> PDF."""

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="PDF → Word", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0)
        )
        ctk.CTkButton(self, text="Selecionar PDF e converter", command=self.convert_pdf_to_docx).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )

        ctk.CTkLabel(self, text="Office → PDF (requer LibreOffice instalado)", font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(20, 0)
        )
        ctk.CTkButton(self, text="Selecionar arquivo e converter", command=self.convert_office_to_pdf).grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )

        self.build_status_label(row=4)

    def convert_pdf_to_docx(self):
        pdf_path = filedialog.askopenfilename(title="Selecione o PDF", filetypes=PDF_EXTENSIONS)
        if not pdf_path:
            return
        default_name = Path(pdf_path).with_suffix(".docx").name
        output_path = filedialog.asksaveasfilename(
            title="Salvar como", defaultextension=".docx", initialfile=default_name
        )
        if not output_path:
            return
        self.run_safely(lambda: office_pdf.pdf_to_docx(pdf_path, output_path))

    def convert_office_to_pdf(self):
        input_path = filedialog.askopenfilename(title="Selecione o arquivo", filetypes=OFFICE_EXTENSIONS)
        if not input_path:
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        self.run_safely(lambda: office_pdf.office_to_pdf(input_path, output_dir))


class ImagePdfTab(BaseTab):
    """Imagens -> PDF e PDF -> Imagens."""

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Imagens → PDF", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0)
        )
        ctk.CTkButton(self, text="Selecionar imagens e converter", command=self.convert_images_to_pdf).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )

        ctk.CTkLabel(self, text="PDF → Imagens", font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(20, 0)
        )
        ctk.CTkButton(self, text="Selecionar PDF e converter", command=self.convert_pdf_to_images).grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )

        self.build_status_label(row=4)

    def convert_images_to_pdf(self):
        image_paths = filedialog.askopenfilenames(title="Selecione as imagens", filetypes=IMAGE_EXTENSIONS)
        if not image_paths:
            return
        output_path = filedialog.asksaveasfilename(
            title="Salvar como", defaultextension=".pdf", initialfile="imagens.pdf"
        )
        if not output_path:
            return
        self.run_safely(lambda: image_pdf.images_to_pdf(list(image_paths), output_path))

    def convert_pdf_to_images(self):
        pdf_path = filedialog.askopenfilename(title="Selecione o PDF", filetypes=PDF_EXTENSIONS)
        if not pdf_path:
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        self.run_safely(lambda: image_pdf.pdf_to_images(pdf_path, output_dir))


class PdfUtilsTab(BaseTab):
    """Juntar, dividir e comprimir PDFs."""

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Juntar PDFs", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0)
        )
        ctk.CTkButton(self, text="Selecionar PDFs e juntar", command=self.merge).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )

        ctk.CTkLabel(self, text="Dividir PDF (uma página por arquivo)", font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(20, 0)
        )
        ctk.CTkButton(self, text="Selecionar PDF e dividir", command=self.split).grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )

        ctk.CTkLabel(self, text="Comprimir PDF", font=ctk.CTkFont(weight="bold")).grid(
            row=4, column=0, columnspan=3, sticky="w", padx=10, pady=(20, 0)
        )
        ctk.CTkButton(self, text="Selecionar PDF e comprimir", command=self.compress).grid(
            row=5, column=0, padx=10, pady=10, sticky="w"
        )

        self.build_status_label(row=6)

    def merge(self):
        pdf_paths = filedialog.askopenfilenames(title="Selecione os PDFs (na ordem desejada)", filetypes=PDF_EXTENSIONS)
        if not pdf_paths:
            return
        output_path = filedialog.asksaveasfilename(
            title="Salvar como", defaultextension=".pdf", initialfile="unido.pdf"
        )
        if not output_path:
            return
        self.run_safely(lambda: pdf_utils.merge_pdfs(list(pdf_paths), output_path))

    def split(self):
        pdf_path = filedialog.askopenfilename(title="Selecione o PDF", filetypes=PDF_EXTENSIONS)
        if not pdf_path:
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        self.run_safely(lambda: pdf_utils.split_pdf(pdf_path, output_dir))

    def compress(self):
        pdf_path = filedialog.askopenfilename(title="Selecione o PDF", filetypes=PDF_EXTENSIONS)
        if not pdf_path:
            return
        default_name = Path(pdf_path).stem + "_comprimido.pdf"
        output_path = filedialog.asksaveasfilename(
            title="Salvar como", defaultextension=".pdf", initialfile=default_name
        )
        if not output_path:
            return
        self.run_safely(lambda: pdf_utils.compress_pdf(pdf_path, output_path))


class ImageConvertTab(BaseTab):
    """Conversão de imagens entre formatos."""

    FORMATS = [".jpg", ".png", ".webp", ".bmp"]

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Converter imagem para outro formato", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0)
        )

        self.format_var = ctk.StringVar(value=self.FORMATS[0])
        ctk.CTkOptionMenu(self, values=self.FORMATS, variable=self.format_var).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        ctk.CTkButton(self, text="Selecionar imagem e converter", command=self.convert).grid(
            row=1, column=1, padx=10, pady=10, sticky="w"
        )

        self.build_status_label(row=2)

    def convert(self):
        input_path = filedialog.askopenfilename(title="Selecione a imagem", filetypes=IMAGE_EXTENSIONS)
        if not input_path:
            return
        target_ext = self.format_var.get()
        default_name = Path(input_path).with_suffix(target_ext).name
        output_path = filedialog.asksaveasfilename(
            title="Salvar como", defaultextension=target_ext, initialfile=default_name
        )
        if not output_path:
            return
        self.run_safely(lambda: image_convert.convert_image(input_path, output_path))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Conversor de Documentos")
        self.geometry("640x480")

        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        tab_names = ["PDF ↔ Office", "Imagens ↔ PDF", "Utilitários de PDF", "Conversão de Imagens"]
        for name in tab_names:
            tabview.add(name)

        PdfOfficeTab(tabview.tab("PDF ↔ Office")).pack(fill="both", expand=True)
        ImagePdfTab(tabview.tab("Imagens ↔ PDF")).pack(fill="both", expand=True)
        PdfUtilsTab(tabview.tab("Utilitários de PDF")).pack(fill="both", expand=True)
        ImageConvertTab(tabview.tab("Conversão de Imagens")).pack(fill="both", expand=True)


def run():
    try:
        app = App()
        app.mainloop()
    except Exception:
        messagebox.showerror("Erro fatal", traceback.format_exc())
        raise
