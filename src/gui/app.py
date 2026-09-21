"""Interface gráfica do Conversor de Documentos."""
import traceback
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

from converters import image_convert, image_pdf, office_pdf, pdf_utils

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

OFFICE_EXTENSIONS = [("Word/Excel/PowerPoint", "*.docx *.xlsx *.pptx")]
PDF_EXTENSIONS = [("PDF", "*.pdf")]
IMAGE_EXTENSIONS = [("Imagens", "*.jpg *.jpeg *.png *.bmp *.webp")]


def _filter_by_extensions(paths, extensions):
    """Mantém apenas os caminhos cuja extensão está em `extensions` (ex: {'.pdf'})."""
    return [p for p in paths if Path(p).suffix.lower() in extensions]


class DropZone(ctk.CTkFrame):
    """Área para arrastar e soltar arquivos, ou clicar para selecionar pelo seletor padrão."""

    def __init__(self, master, filetypes, extensions, on_files, multiple=True, hint=None):
        super().__init__(master, border_width=2, border_color=("gray70", "gray35"), corner_radius=8)
        self.filetypes = filetypes
        self.extensions = extensions
        self.on_files = on_files
        self.multiple = multiple
        self.default_hint = hint or (
            "Arraste os arquivos aqui, ou clique para selecionar"
            if multiple
            else "Arraste o arquivo aqui, ou clique para selecionar"
        )

        self.label = ctk.CTkLabel(self, text=self.default_hint, text_color="gray", justify="center")
        self.label.pack(expand=True, fill="both", padx=12, pady=14)

        for widget in (self, self.label):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._handle_drop)
            widget.bind("<Button-1>", self._handle_click)

    def _handle_drop(self, event):
        paths = list(self.tk.splitlist(event.data))
        self._dispatch(paths)

    def _handle_click(self, _event=None):
        if self.multiple:
            paths = list(filedialog.askopenfilenames(title="Selecione os arquivos", filetypes=self.filetypes))
        else:
            single = filedialog.askopenfilename(title="Selecione o arquivo", filetypes=self.filetypes)
            paths = [single] if single else []
        self._dispatch(paths)

    def _dispatch(self, paths):
        paths = _filter_by_extensions(paths, self.extensions)
        if not paths:
            return
        if not self.multiple:
            paths = paths[:1]
        self.set_selected(paths)
        self.on_files(paths)

    def set_selected(self, paths):
        if not paths:
            self.label.configure(text=self.default_hint, text_color="gray")
            return
        if len(paths) == 1:
            text = Path(paths[0]).name
        else:
            text = f"{len(paths)} arquivos selecionados"
        self.label.configure(text=text, text_color=("black", "white"))


class BaseTab(ctk.CTkFrame):
    """Frame base com um log de status compartilhado por todas as abas."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.status_box = None

    def build_status_box(self, row: int, height: int = 90):
        self.grid_rowconfigure(row, weight=1)
        self.status_box = ctk.CTkTextbox(self, height=height)
        self.status_box.grid(row=row, column=0, columnspan=3, sticky="nsew", padx=10, pady=(10, 10))
        self.status_box.configure(state="disabled")

    def log(self, text: str):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", text + "\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")

    def clear_log(self):
        self.status_box.configure(state="normal")
        self.status_box.delete("1.0", "end")
        self.status_box.configure(state="disabled")

    def run_batch(self, paths, convert_one):
        """Chama `convert_one(path)` para cada arquivo, sem parar o lote em caso de erro."""
        self.clear_log()
        if not paths:
            self.log("Nenhum arquivo selecionado.")
            return
        successes = 0
        for path in paths:
            name = Path(path).name
            try:
                convert_one(path)
            except Exception as exc:  # noqa: BLE001 - erro é reportado ao usuário, não silenciado
                self.log(f"✗ {name}: {exc}")
                traceback.print_exc()
            else:
                successes += 1
                self.log(f"✓ {name}")
        self.log(f"--- {successes}/{len(paths)} arquivo(s) concluído(s) ---")


class PdfOfficeTab(BaseTab):
    """PDF -> Word e Word/Excel/PowerPoint -> PDF, em lote."""

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.pdf_files = []
        self.office_files = []

        ctk.CTkLabel(self, text="PDF → Word", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_pdf_files).grid(
            row=1, column=0, sticky="ew", padx=10, pady=6
        )
        ctk.CTkButton(self, text="Converter para Word", command=self.convert_pdf_to_docx).grid(
            row=2, column=0, sticky="w", padx=10
        )

        ctk.CTkLabel(
            self, text="Office → PDF (requer LibreOffice instalado)", font=ctk.CTkFont(weight="bold")
        ).grid(row=3, column=0, sticky="w", padx=10, pady=(18, 0))
        DropZone(self, OFFICE_EXTENSIONS, {".docx", ".xlsx", ".pptx"}, self._set_office_files).grid(
            row=4, column=0, sticky="ew", padx=10, pady=6
        )
        ctk.CTkButton(self, text="Converter para PDF", command=self.convert_office_to_pdf).grid(
            row=5, column=0, sticky="w", padx=10
        )

        self.build_status_box(row=6)

    def _set_pdf_files(self, paths):
        self.pdf_files = paths

    def _set_office_files(self, paths):
        self.office_files = paths

    def convert_pdf_to_docx(self):
        if not self.pdf_files:
            self.clear_log()
            self.log("Selecione ao menos um PDF primeiro.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return

        def convert_one(path):
            out_path = str(Path(output_dir) / Path(path).with_suffix(".docx").name)
            office_pdf.pdf_to_docx(path, out_path)

        self.run_batch(self.pdf_files, convert_one)

    def convert_office_to_pdf(self):
        if not self.office_files:
            self.clear_log()
            self.log("Selecione ao menos um arquivo do Office primeiro.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        self.run_batch(self.office_files, lambda path: office_pdf.office_to_pdf(path, output_dir))


class ImagePdfTab(BaseTab):
    """Imagens -> PDF e PDF -> Imagens, em lote."""

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.image_files = []
        self.pdf_files = []

        ctk.CTkLabel(self, text="Imagens → PDF (uma única página por imagem)", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 0)
        )
        DropZone(self, IMAGE_EXTENSIONS, {".jpg", ".jpeg", ".png", ".bmp", ".webp"}, self._set_image_files).grid(
            row=1, column=0, sticky="ew", padx=10, pady=6
        )
        ctk.CTkButton(self, text="Juntar imagens em um PDF", command=self.convert_images_to_pdf).grid(
            row=2, column=0, sticky="w", padx=10
        )

        ctk.CTkLabel(self, text="PDF → Imagens", font=ctk.CTkFont(weight="bold")).grid(
            row=3, column=0, sticky="w", padx=10, pady=(18, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_pdf_files).grid(
            row=4, column=0, sticky="ew", padx=10, pady=6
        )
        ctk.CTkButton(self, text="Extrair páginas como imagens", command=self.convert_pdf_to_images).grid(
            row=5, column=0, sticky="w", padx=10
        )

        self.build_status_box(row=6)

    def _set_image_files(self, paths):
        self.image_files = paths

    def _set_pdf_files(self, paths):
        self.pdf_files = paths

    def convert_images_to_pdf(self):
        if not self.image_files:
            self.clear_log()
            self.log("Selecione ao menos uma imagem primeiro.")
            return
        output_path = filedialog.asksaveasfilename(
            title="Salvar como", defaultextension=".pdf", initialfile="imagens.pdf"
        )
        if not output_path:
            return
        self.clear_log()
        try:
            image_pdf.images_to_pdf(self.image_files, output_path)
        except Exception as exc:  # noqa: BLE001
            self.log(f"✗ Erro: {exc}")
            traceback.print_exc()
        else:
            self.log(f"✓ PDF criado com {len(self.image_files)} página(s): {Path(output_path).name}")

    def convert_pdf_to_images(self):
        if not self.pdf_files:
            self.clear_log()
            self.log("Selecione ao menos um PDF primeiro.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        self.run_batch(self.pdf_files, lambda path: image_pdf.pdf_to_images(path, output_dir))


class PdfUtilsTab(BaseTab):
    """Juntar, dividir, comprimir e rotacionar PDFs."""

    ROTATIONS = ["90°", "180°", "270°"]

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.merge_files = []
        self.split_file = []
        self.compress_files = []
        self.rotate_files = []

        ctk.CTkLabel(self, text="Juntar PDFs (na ordem selecionada)", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_merge_files).grid(
            row=1, column=0, sticky="ew", padx=10, pady=6
        )
        ctk.CTkButton(self, text="Juntar e salvar", command=self.merge).grid(row=2, column=0, sticky="w", padx=10)

        ctk.CTkLabel(self, text="Dividir PDF (uma página por arquivo)", font=ctk.CTkFont(weight="bold")).grid(
            row=3, column=0, sticky="w", padx=10, pady=(18, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_split_file, multiple=False).grid(
            row=4, column=0, sticky="ew", padx=10, pady=6
        )
        ctk.CTkButton(self, text="Dividir", command=self.split).grid(row=5, column=0, sticky="w", padx=10)

        ctk.CTkLabel(self, text="Comprimir PDFs", font=ctk.CTkFont(weight="bold")).grid(
            row=6, column=0, sticky="w", padx=10, pady=(18, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_compress_files).grid(
            row=7, column=0, sticky="ew", padx=10, pady=6
        )
        ctk.CTkButton(self, text="Comprimir", command=self.compress).grid(row=8, column=0, sticky="w", padx=10)

        ctk.CTkLabel(self, text="Rotacionar páginas", font=ctk.CTkFont(weight="bold")).grid(
            row=9, column=0, sticky="w", padx=10, pady=(18, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_rotate_files).grid(
            row=10, column=0, sticky="ew", padx=10, pady=6
        )
        rotate_row = ctk.CTkFrame(self, fg_color="transparent")
        rotate_row.grid(row=11, column=0, sticky="w", padx=10)
        self.rotation_var = ctk.StringVar(value=self.ROTATIONS[0])
        ctk.CTkOptionMenu(rotate_row, values=self.ROTATIONS, variable=self.rotation_var, width=90).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(rotate_row, text="Rotacionar", command=self.rotate).pack(side="left")

        self.build_status_box(row=12)

    def _set_merge_files(self, paths):
        self.merge_files = paths

    def _set_split_file(self, paths):
        self.split_file = paths

    def _set_compress_files(self, paths):
        self.compress_files = paths

    def _set_rotate_files(self, paths):
        self.rotate_files = paths

    def merge(self):
        if len(self.merge_files) < 2:
            self.clear_log()
            self.log("Selecione ao menos dois PDFs para juntar.")
            return
        output_path = filedialog.asksaveasfilename(
            title="Salvar como", defaultextension=".pdf", initialfile="unido.pdf"
        )
        if not output_path:
            return
        self.clear_log()
        try:
            pdf_utils.merge_pdfs(self.merge_files, output_path)
        except Exception as exc:  # noqa: BLE001
            self.log(f"✗ Erro: {exc}")
            traceback.print_exc()
        else:
            self.log(f"✓ PDFs juntados em: {Path(output_path).name}")

    def split(self):
        if not self.split_file:
            self.clear_log()
            self.log("Selecione um PDF primeiro.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        self.run_batch(self.split_file, lambda path: pdf_utils.split_pdf(path, output_dir))

    def compress(self):
        if not self.compress_files:
            self.clear_log()
            self.log("Selecione ao menos um PDF primeiro.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return

        def convert_one(path):
            out_path = str(Path(output_dir) / f"{Path(path).stem}_comprimido.pdf")
            pdf_utils.compress_pdf(path, out_path)

        self.run_batch(self.compress_files, convert_one)

    def rotate(self):
        if not self.rotate_files:
            self.clear_log()
            self.log("Selecione ao menos um PDF primeiro.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        degrees = int(self.rotation_var.get().rstrip("°"))

        def convert_one(path):
            out_path = str(Path(output_dir) / f"{Path(path).stem}_rotacionado.pdf")
            pdf_utils.rotate_pages(path, out_path, degrees)

        self.run_batch(self.rotate_files, convert_one)


class PdfSecurityTab(BaseTab):
    """Proteger/remover senha e adicionar marca d'água em PDFs."""

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.protect_files = []
        self.unprotect_files = []
        self.watermark_files = []

        ctk.CTkLabel(self, text="Proteger PDFs com senha", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_protect_files).grid(
            row=1, column=0, sticky="ew", padx=10, pady=6
        )
        protect_row = ctk.CTkFrame(self, fg_color="transparent")
        protect_row.grid(row=2, column=0, sticky="w", padx=10)
        self.protect_password_entry = ctk.CTkEntry(protect_row, placeholder_text="Senha", show="•", width=160)
        self.protect_password_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(protect_row, text="Proteger", command=self.protect).pack(side="left")

        ctk.CTkLabel(self, text="Remover senha de PDFs", font=ctk.CTkFont(weight="bold")).grid(
            row=3, column=0, sticky="w", padx=10, pady=(18, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_unprotect_files).grid(
            row=4, column=0, sticky="ew", padx=10, pady=6
        )
        unprotect_row = ctk.CTkFrame(self, fg_color="transparent")
        unprotect_row.grid(row=5, column=0, sticky="w", padx=10)
        self.unprotect_password_entry = ctk.CTkEntry(unprotect_row, placeholder_text="Senha atual", show="•", width=160)
        self.unprotect_password_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(unprotect_row, text="Remover senha", command=self.unprotect).pack(side="left")

        ctk.CTkLabel(self, text="Adicionar marca d'água", font=ctk.CTkFont(weight="bold")).grid(
            row=6, column=0, sticky="w", padx=10, pady=(18, 0)
        )
        DropZone(self, PDF_EXTENSIONS, {".pdf"}, self._set_watermark_files).grid(
            row=7, column=0, sticky="ew", padx=10, pady=6
        )
        watermark_row = ctk.CTkFrame(self, fg_color="transparent")
        watermark_row.grid(row=8, column=0, sticky="w", padx=10)
        self.watermark_text_entry = ctk.CTkEntry(watermark_row, placeholder_text="Texto da marca d'água", width=200)
        self.watermark_text_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(watermark_row, text="Aplicar", command=self.watermark).pack(side="left")

        self.build_status_box(row=9)

    def _set_protect_files(self, paths):
        self.protect_files = paths

    def _set_unprotect_files(self, paths):
        self.unprotect_files = paths

    def _set_watermark_files(self, paths):
        self.watermark_files = paths

    def protect(self):
        if not self.protect_files:
            self.clear_log()
            self.log("Selecione ao menos um PDF primeiro.")
            return
        password = self.protect_password_entry.get()
        if not password:
            self.clear_log()
            self.log("Digite uma senha.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return

        def convert_one(path):
            out_path = str(Path(output_dir) / f"{Path(path).stem}_protegido.pdf")
            pdf_utils.add_password(path, password, out_path)

        self.run_batch(self.protect_files, convert_one)

    def unprotect(self):
        if not self.unprotect_files:
            self.clear_log()
            self.log("Selecione ao menos um PDF primeiro.")
            return
        password = self.unprotect_password_entry.get()
        if not password:
            self.clear_log()
            self.log("Digite a senha atual do PDF.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return

        def convert_one(path):
            out_path = str(Path(output_dir) / f"{Path(path).stem}_sem_senha.pdf")
            pdf_utils.remove_password(path, password, out_path)

        self.run_batch(self.unprotect_files, convert_one)

    def watermark(self):
        if not self.watermark_files:
            self.clear_log()
            self.log("Selecione ao menos um PDF primeiro.")
            return
        text = self.watermark_text_entry.get()
        if not text:
            self.clear_log()
            self.log("Digite o texto da marca d'água.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return

        def convert_one(path):
            out_path = str(Path(output_dir) / f"{Path(path).stem}_marcado.pdf")
            pdf_utils.add_watermark(path, out_path, text)

        self.run_batch(self.watermark_files, convert_one)


class ImageConvertTab(BaseTab):
    """Conversão de imagens entre formatos, em lote."""

    FORMATS = [".jpg", ".png", ".webp", ".bmp"]

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.image_files = []

        ctk.CTkLabel(self, text="Converter imagens para outro formato", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 0)
        )
        DropZone(self, IMAGE_EXTENSIONS, {".jpg", ".jpeg", ".png", ".bmp", ".webp"}, self._set_image_files).grid(
            row=1, column=0, sticky="ew", padx=10, pady=6
        )

        options_row = ctk.CTkFrame(self, fg_color="transparent")
        options_row.grid(row=2, column=0, sticky="w", padx=10)
        self.format_var = ctk.StringVar(value=self.FORMATS[0])
        ctk.CTkOptionMenu(options_row, values=self.FORMATS, variable=self.format_var, width=90).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(options_row, text="Converter", command=self.convert).pack(side="left")

        self.build_status_box(row=3)

    def _set_image_files(self, paths):
        self.image_files = paths

    def convert(self):
        if not self.image_files:
            self.clear_log()
            self.log("Selecione ao menos uma imagem primeiro.")
            return
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        target_ext = self.format_var.get()

        def convert_one(path):
            out_path = str(Path(output_dir) / Path(path).with_suffix(target_ext).name)
            image_convert.convert_image(path, out_path)

        self.run_batch(self.image_files, convert_one)


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Conversor de Documentos")
        self.geometry("700x560")

        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        tab_names = ["PDF ↔ Office", "Imagens ↔ PDF", "Utilitários de PDF", "Segurança de PDF", "Conversão de Imagens"]
        for name in tab_names:
            tabview.add(name)

        PdfOfficeTab(tabview.tab("PDF ↔ Office")).pack(fill="both", expand=True)
        ImagePdfTab(tabview.tab("Imagens ↔ PDF")).pack(fill="both", expand=True)
        PdfUtilsTab(tabview.tab("Utilitários de PDF")).pack(fill="both", expand=True)
        PdfSecurityTab(tabview.tab("Segurança de PDF")).pack(fill="both", expand=True)
        ImageConvertTab(tabview.tab("Conversão de Imagens")).pack(fill="both", expand=True)


def run():
    try:
        app = App()
        app.mainloop()
    except Exception:
        messagebox.showerror("Erro fatal", traceback.format_exc())
        raise
