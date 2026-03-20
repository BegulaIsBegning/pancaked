#!/usr/bin/env bash
# ============================================================
# Script de Instalação - DevNotes v2.1.0
# Gerado pelo LocalStore
# ============================================================
set -e

APP_NAME="DevNotes"
APP_ID="devnotes"
APP_VERSION="2.1.0"
INSTALL_DIR="/opt/${APP_ID}"
BIN_LINK="/usr/local/bin/${APP_ID}"
DESKTOP_FILE="/usr/share/applications/${APP_ID}.desktop"

# Cores
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Instalando ${APP_NAME} v${APP_VERSION}          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# Verificar root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}[ERRO]${NC} Execute com sudo: sudo bash install-${APP_ID}.sh"
    exit 1
fi

# Detectar distro para dependências
detect_pkg_manager() {
    if command -v apt-get &>/dev/null; then echo "apt"
    elif command -v dnf &>/dev/null; then echo "dnf"
    elif command -v pacman &>/dev/null; then echo "pacman"
    else echo "unknown"; fi
}

PKG_MGR=$(detect_pkg_manager)

echo -e "[1/5] ${YELLOW}Verificando dependências...${NC}"
# Exemplo: instalar dependência se necessário
# if ! command -v python3 &>/dev/null; then
#     [ "$PKG_MGR" = "apt" ] && apt-get install -y python3
# fi

echo -e "[2/5] ${YELLOW}Criando diretório em ${INSTALL_DIR}...${NC}"
mkdir -p "${INSTALL_DIR}"

echo -e "[3/5] ${YELLOW}Instalando arquivos do ${APP_NAME}...${NC}"

# Criar executável principal (simulado)
cat > "${INSTALL_DIR}/${APP_ID}" << 'APPEOF'
#!/usr/bin/env bash
echo "DevNotes v2.1.0 iniciado!"
echo "Pressione Ctrl+C para sair."
while true; do sleep 1; done
APPEOF
chmod +x "${INSTALL_DIR}/${APP_ID}"

# Criar configuração padrão
cat > "${INSTALL_DIR}/config.json" << CONFEOF
{
  "version": "${APP_VERSION}",
  "theme": "dark",
  "font_size": 14,
  "auto_save": true,
  "data_dir": "${HOME}/.config/${APP_ID}"
}
CONFEOF

# Criar link simbólico
echo -e "[4/5] ${YELLOW}Criando link em ${BIN_LINK}...${NC}"
ln -sf "${INSTALL_DIR}/${APP_ID}" "${BIN_LINK}"

# Criar entrada .desktop para o menu de aplicativos
echo -e "[5/5] ${YELLOW}Registrando no menu de aplicativos...${NC}"
cat > "${DESKTOP_FILE}" << DESKEOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Comment=Editor de notas para desenvolvedores
Exec=${BIN_LINK}
Icon=${INSTALL_DIR}/icon.png
Categories=Utility;TextEditor;Development;
Terminal=false
StartupNotify=true
DESKEOF

# Atualizar cache de ícones se disponível
command -v update-desktop-database &>/dev/null && update-desktop-database /usr/share/applications/ || true

echo ""
echo -e "${GREEN}✓ ${APP_NAME} instalado com sucesso!${NC}"
echo -e "  Localização: ${INSTALL_DIR}"
echo -e "  Comando:     ${APP_ID}"
echo ""
