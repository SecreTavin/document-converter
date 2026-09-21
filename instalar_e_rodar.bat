@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "DIST_EXE=dist\ConversorDeDocumentos.exe"

if exist "%DIST_EXE%" (
    echo Abrindo o Conversor de Documentos...
    start "" "%DIST_EXE%"
    exit /b 0
)

echo ============================================================
echo   Configurando o Conversor de Documentos (primeira vez)
echo   Isso pode levar alguns minutos. Nas proximas vezes o
echo   programa abrira direto, sem passar por isso de novo.
echo ============================================================
echo.

set "PYTHON_CMD="
where python >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
    where py >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py"
)

if not defined PYTHON_CMD (
    echo [ERRO] Python nao foi encontrado neste computador.
    echo.
    echo 1. Baixe o Python em: https://www.python.org/downloads/
    echo 2. Durante a instalacao, marque a opcao "Add python.exe to PATH".
    echo 3. Depois de instalar, execute este arquivo novamente.
    echo.
    pause
    exit /b 1
)

if not exist venv (
    echo Criando ambiente virtual...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
)

echo Instalando dependencias, aguarde...
venv\Scripts\python.exe -m pip install --upgrade pip -q
venv\Scripts\python.exe -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERRO] Falha ao instalar as dependencias. Verifique sua conexao com a internet.
    pause
    exit /b 1
)

set "LIBREOFFICE_OK=0"
where soffice >nul 2>nul
if not errorlevel 1 set "LIBREOFFICE_OK=1"
if exist "%ProgramFiles%\LibreOffice\program\soffice.exe" set "LIBREOFFICE_OK=1"
if exist "%ProgramFiles(x86)%\LibreOffice\program\soffice.exe" set "LIBREOFFICE_OK=1"

if "%LIBREOFFICE_OK%"=="0" (
    echo.
    echo [AVISO] LibreOffice nao foi encontrado neste computador.
    echo Ele so e necessario para converter Word/Excel/PowerPoint em PDF.
    echo As demais conversoes funcionam normalmente sem ele.
    echo Para instalar: https://www.libreoffice.org/download/
    echo.
)

echo Gerando o programa (ConversorDeDocumentos.exe)...
venv\Scripts\pyinstaller.exe --name "ConversorDeDocumentos" --windowed --onefile --noconfirm --collect-all tkinterdnd2 --collect-all numpy src\main.py
if errorlevel 1 (
    echo [ERRO] Nao foi possivel gerar o executavel. Veja as mensagens acima.
    pause
    exit /b 1
)

if exist "%DIST_EXE%" (
    echo.
    echo Tudo pronto! Abrindo o Conversor de Documentos...
    echo Dica: crie um atalho de "%DIST_EXE%" na Area de Trabalho para
    echo abrir o programa direto nas proximas vezes, sem precisar deste arquivo.
    start "" "%DIST_EXE%"
) else (
    echo [ERRO] O executavel nao foi criado. Veja as mensagens acima.
    pause
)
