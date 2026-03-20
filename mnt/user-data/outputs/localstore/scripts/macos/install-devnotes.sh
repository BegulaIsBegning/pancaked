#!/usr/bin/env bash
# ============================================================
# Script de Instalação - DevNotes v2.1.0 (macOS)
# Gerado pelo LocalStore
# ============================================================
set -e

APP_NAME="DevNotes"
APP_ID="devnotes"
APP_VERSION="2.1.0"
INSTALL_DIR="/Applications/${APP_NAME}.app"
CONTENTS_DIR="${INSTALL_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Instalando ${APP_NAME} v${APP_VERSION}          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

echo -e "[1/5] ${YELLOW}Verificando macOS...${NC}"
OS_VER=$(sw_vers -productVersion)
echo "  macOS $OS_VER detectado."

echo -e "[2/5] ${YELLOW}Criando bundle .app em /Applications...${NC}"
mkdir -p "${MACOS_DIR}" "${RESOURCES_DIR}"

echo -e "[3/5] ${YELLOW}Instalando arquivos do ${APP_NAME}...${NC}"

# Criar executável principal
cat > "${MACOS_DIR}/${APP_NAME}" << 'APPEOF'
#!/usr/bin/env bash
echo "DevNotes v2.1.0 iniciado no macOS!"
APPEOF
chmod +x "${MACOS_DIR}/${APP_NAME}"

# Criar Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.localstore.${APP_ID}</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleVersion</key>
    <string>${APP_VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${APP_VERSION}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLISTEOF

# Configuração padrão
mkdir -p "${HOME}/Library/Application Support/${APP_NAME}"
cat > "${HOME}/Library/Application Support/${APP_NAME}/config.json" << CONFEOF
{
  "version": "${APP_VERSION}",
  "theme": "dark",
  "font_size": 14,
  "auto_save": true
}
CONFEOF

echo -e "[4/5] ${YELLOW}Registrando no Launch Services...${NC}"
# Atualizar banco de dados de aplicativos
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister \
    -f "${INSTALL_DIR}" 2>/dev/null || true

echo -e "[5/5] ${YELLOW}Criando link de linha de comando...${NC}"
ln -sf "${MACOS_DIR}/${APP_NAME}" "/usr/local/bin/${APP_ID}" 2>/dev/null || \
    echo "  (Opcional: adicione manualmente ao PATH)"

echo ""
echo -e "${GREEN}✓ ${APP_NAME} instalado em /Applications/${APP_NAME}.app${NC}"
echo -e "  Abra o Finder > Applications para acessá-lo."
echo ""
