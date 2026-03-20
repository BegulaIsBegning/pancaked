#!/usr/bin/env bash
# ============================================================
# Template genérico de instalação — Linux
# ============================================================
set -euo pipefail

APP_NAME="NomeDoApp"
APP_ID="nomeDoApp"
APP_VERSION="1.0.0"
INSTALL_DIR="/opt/${APP_ID}"
BIN_LINK="/usr/local/bin/${APP_ID}"
DESKTOP_FILE="/usr/share/applications/${APP_ID}.desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

[[ $EUID -ne 0 ]] && { echo -e "${RED}[ERRO]${NC} Execute com sudo."; exit 1; }

echo -e "\n${GREEN}┌──────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  LocalStore — Instalando ${APP_NAME}${NC}"
echo -e "${GREEN}└──────────────────────────────────────┘${NC}\n"

echo -e "[1/4] ${YELLOW}Criando /opt/${APP_ID}...${NC}"
mkdir -p "${INSTALL_DIR}"

echo -e "[2/4] ${YELLOW}Copiando arquivos...${NC}"
cp -r "${SCRIPT_DIR}/extracted/." "${INSTALL_DIR}/"
chmod +x "${INSTALL_DIR}/${APP_ID}" 2>/dev/null || true

echo -e "[3/4] ${YELLOW}Criando link simbólico...${NC}"
ln -sf "${INSTALL_DIR}/${APP_ID}" "${BIN_LINK}"

echo -e "[4/4] ${YELLOW}Criando entrada .desktop...${NC}"
cat > "${DESKTOP_FILE}" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Exec=${BIN_LINK} %U
Icon=${INSTALL_DIR}/icon.png
Comment=${APP_NAME} v${APP_VERSION}
Categories=Utility;
Terminal=false
StartupNotify=true
EOF
command -v update-desktop-database &>/dev/null && update-desktop-database "${DESKTOP_FILE%/*}" || true

echo -e "\n${GREEN}✅  ${APP_NAME} instalado com sucesso!${NC}"
echo -e "   Comando: ${APP_ID}\n"
