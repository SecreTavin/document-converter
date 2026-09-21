# Conversor de Documentos

Conversor de arquivos local (offline) para não depender de ferramentas web como o
iLovePDF ao lidar com documentos sensíveis. Todo o processamento acontece no seu
computador — nenhum arquivo é enviado para a internet.

## Funcionalidades

- **PDF ↔ Office**: PDF → Word (sem dependências externas) e Word/Excel/PowerPoint → PDF
  (via LibreOffice headless).
- **Imagens ↔ PDF**: juntar imagens em um PDF e extrair páginas de um PDF como imagens.
- **Utilitários de PDF**: juntar, dividir, comprimir e rotacionar páginas.
- **Segurança de PDF**: proteger com senha, remover senha e adicionar marca d'água.
- **OCR**: reconhece o texto de PDFs escaneados, gerando um PDF pesquisável ou
  extraindo o texto para Word.
- **Conversão de imagens**: JPG ↔ PNG ↔ WEBP ↔ BMP.
- **Conversão em lote**: todas as operações acima aceitam vários arquivos de uma vez.
- **Arrastar e soltar**: arraste os arquivos direto para a janela do programa, ou
  clique para escolher pelo seletor de arquivos de sempre.

## Requisitos

- Python 3.11+
- [LibreOffice](https://www.libreoffice.org/download/) instalado (apenas necessário
  para converter Word/Excel/PowerPoint → PDF)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) instalado (apenas
  necessário para a aba de OCR). No macOS: `brew install tesseract tesseract-lang`.

## Configuração do ambiente

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Executar em modo desenvolvimento

```bash
python src/main.py
```

## Gerar o executável

### macOS

```bash
pyinstaller --name "ConversorDeDocumentos" --windowed --onefile --icon assets/icon.icns --collect-all tkinterdnd2 --collect-all numpy src/main.py
```

O app fica em `dist/ConversorDeDocumentos.app`.

### Windows

```bash
pyinstaller --name "ConversorDeDocumentos" --windowed --onefile --icon assets\icon.ico --collect-all tkinterdnd2 --collect-all numpy src/main.py
```

O executável fica em `dist/ConversorDeDocumentos.exe` (um único arquivo).

> - `--collect-all tkinterdnd2` é necessário para o recurso de arrastar-e-soltar
>   funcionar no executável empacotado (ele usa uma extensão nativa do Tcl/Tk que o
>   PyInstaller não inclui por padrão).
> - `--collect-all numpy` evita um erro comum de importação do NumPy quando
>   empacotado (`ModuleNotFoundError: No module named 'numpy._core._exceptions'`).
> - `--onefile` (em vez de `--onedir`) evita um bug conhecido do PyInstaller com o
>   OpenCV (dependência do `pdf2docx`), que faz o app travar ao abrir com o erro
>   "recursion is detected during loading of cv2 binary extensions" quando os
>   arquivos ficam divididos em pastas separadas.

> O build precisa ser feito em cada sistema operacional separadamente (o PyInstaller
> não faz cross-compilation). Ou seja: gere o `.app` rodando no Mac e o `.exe` rodando
> em uma máquina Windows.

### macOS — gerar o `.dmg` pronto para distribuir

```bash
./build_macos.sh
```

Gera `dist/ConversorDeDocumentos.app` e empacota em `dist/ConversorDeDocumentos.dmg`
(com um atalho para a pasta Aplicativos, como qualquer instalador de app do Mac).
Como o app não é assinado com um certificado de desenvolvedor Apple, ao abrir pela
primeira vez pode aparecer um aviso do Gatekeeper — clique com o botão direito no
app → **Abrir** → **Abrir mesmo assim**.

### Windows — instalador `.exe` (opcional, mais "profissional")

Além do `instalar_e_rodar.bat` (que já resolve tudo sozinho), dá para gerar um
instalador de verdade, com atalho no Menu Iniciar e desinstalador:

1. Gere `dist/ConversorDeDocumentos.exe` (via `instalar_e_rodar.bat` ou o comando
   pyinstaller acima).
2. Instale o [Inno Setup](https://jrsoftware.org/isinfo.php) (gratuito).
3. Abra `installer_windows.iss` com o Inno Setup Compiler e clique em **Compile**.
4. O instalador final fica em `installer_output/ConversorDeDocumentos_Setup.exe`.

> Esse passo é opcional e precisa ser feito em uma máquina Windows (o Inno Setup só
> roda no Windows, não foi possível testar esse `.iss` a partir do Mac). Para o uso
> do dia a dia, o `instalar_e_rodar.bat` já é suficiente.

### Windows — jeito simples (para quem não mexe com programação)

Copie a pasta inteira do projeto para o PC com Windows (via pendrive, Google Drive,
WeTransfer, etc.) e dê duplo clique em **`instalar_e_rodar.bat`**.

Na primeira vez, o script sozinho:

1. Confere se o Python está instalado (se não estiver, ele avisa e dá o link para instalar).
2. Cria o ambiente virtual e instala todas as dependências.
3. Gera o `ConversorDeDocumentos.exe` dentro de `dist/`.
4. Abre o programa automaticamente.

Da segunda vez em diante, dar duplo clique no `.bat` (ou direto no `.exe` gerado)
já abre o programa na hora, sem repetir a instalação. Vale criar um atalho do
`dist/ConversorDeDocumentos.exe` na Área de Trabalho.

Se aparecer o aviso do Windows Defender/SmartScreen ("Windows protegeu o computador"),
é porque o executável não é assinado digitalmente (normal para apps caseiros) — basta
clicar em **"Mais informações" → "Executar assim mesmo"**.

## Estrutura do projeto

```
src/
  main.py              # ponto de entrada
  gui/
    app.py             # interface (CustomTkinter + arrastar-e-soltar)
  converters/
    office_pdf.py       # PDF <-> Word/Excel/PowerPoint
    image_pdf.py         # Imagens <-> PDF
    pdf_utils.py          # juntar/dividir/comprimir/rotacionar/senha/marca d'água
    ocr.py                 # OCR de PDFs escaneados
    image_convert.py       # conversão entre formatos de imagem
```

## Roadmap

- [ ] Suporte a Excel/PowerPoint → estrutura editável (hoje só PDF → Word tem
      reconstrução de layout completa)
- [ ] Compressão de PDF com controle de qualidade de imagem
- [ ] Reordenar páginas pela interface (a função já existe em `pdf_utils.reorder_pages`)
