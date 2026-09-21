#!/bin/bash
# Gera o ConversorDeDocumentos.app e empacota em um .dmg pronto para distribuir.
set -euo pipefail
cd "$(dirname "$0")"

APP_NAME="ConversorDeDocumentos"
VENV_PYINSTALLER="venv/bin/pyinstaller"

if [ ! -x "$VENV_PYINSTALLER" ]; then
    echo "[ERRO] Ambiente virtual não encontrado. Rode primeiro:"
    echo "  python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

rm -rf build dist "${APP_NAME}.spec"

echo "Gerando ${APP_NAME}.app..."
"$VENV_PYINSTALLER" --name "$APP_NAME" --windowed --onefile --noconfirm \
    --icon assets/icon.icns \
    --collect-all tkinterdnd2 --collect-all numpy \
    src/main.py

echo "Criando ${APP_NAME}.dmg..."
rm -f "dist/${APP_NAME}.dmg"
DMG_STAGING=$(mktemp -d)
cp -R "dist/${APP_NAME}.app" "$DMG_STAGING/"
ln -s /Applications "$DMG_STAGING/Aplicativos"

hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_STAGING" -ov -format UDZO "dist/${APP_NAME}.dmg"
rm -rf "$DMG_STAGING"

echo
echo "Pronto: dist/${APP_NAME}.dmg"
echo "Basta abrir o .dmg e arrastar o app para a pasta Aplicativos."
