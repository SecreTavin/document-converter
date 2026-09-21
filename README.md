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
- **Conversão de imagens**: JPG ↔ PNG ↔ WEBP ↔ BMP.
- **Conversão em lote**: todas as operações acima aceitam vários arquivos de uma vez.
- **Arrastar e soltar**: arraste os arquivos direto para a janela do programa, ou
  clique para escolher pelo seletor de arquivos de sempre.

## Requisitos

- Python 3.11+
- [LibreOffice](https://www.libreoffice.org/download/) instalado (apenas necessário
  para converter Word/Excel/PowerPoint → PDF)

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
pyinstaller --name "ConversorDeDocumentos" --windowed --onefile --collect-all tkinterdnd2 --collect-all numpy src/main.py
```

O app fica em `dist/ConversorDeDocumentos.app`.

### Windows

```bash
pyinstaller --name "ConversorDeDocumentos" --windowed --onefile --collect-all tkinterdnd2 --collect-all numpy src/main.py
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

### Windows — jeito simples (para quem não mexe com programação)

Copie a pasta inteira do projeto para o PC com Windows (via pendrive, Google Drive,
WeTransfer, etc.) e dê duplo clique em **`instalar_e_rodar.bat`**.

Na primeira vez, o script sozinho:

1. Confere se o Python está instalado (se não estiver, ele avisa e dá o link para instalar).
2. Cria o ambiente virtual e instala todas as dependências.
3. Gera o `ConversorDeDocumentos.exe` dentro de `dist/ConversorDeDocumentos/`.
4. Abre o programa automaticamente.

Da segunda vez em diante, dar duplo clique no `.bat` (ou direto no `.exe` gerado)
já abre o programa na hora, sem repetir a instalação. Vale criar um atalho do
`dist/ConversorDeDocumentos/ConversorDeDocumentos.exe` na Área de Trabalho.

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
    image_convert.py       # conversão entre formatos de imagem
```

## Roadmap

- [ ] OCR para PDFs escaneados (torná-los pesquisáveis e convertíveis para Word)
- [ ] Suporte a Excel/PowerPoint → estrutura editável (hoje só PDF → Word tem
      reconstrução de layout completa)
- [ ] Compressão de PDF com controle de qualidade de imagem
- [ ] Reordenar páginas pela interface (a função já existe em `pdf_utils.reorder_pages`)
- [ ] Ícone e instalador (.dmg / .msi)
