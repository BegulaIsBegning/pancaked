# 📦 LocalStore — App Store Local baseada em GitHub

> Sistema de distribuição de aplicativos desktop que usa o GitHub como backend.
> Sem servidores próprios. Sem banco de dados. Só GitHub + JSON + Python.

---

## 🚀 Como rodar

### Pré-requisitos
- Python 3.8+ (sem dependências externas — usa apenas stdlib)
- Tkinter (incluído no Python padrão; no Ubuntu: `sudo apt install python3-tk`)

### Primeira execução
```bash
# Clone ou baixe este repositório
git clone https://github.com/SEU_USUARIO/localstore
cd localstore

# Edite a URL do catálogo no topo de localstore.py:
# CATALOG_URL = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/data/apps.json"

# Rode
python localstore.py
```

---

## 📁 Estrutura de pastas

```
localstore/
├── localstore.py              ← App principal (ÚNICO arquivo para rodar)
│
├── data/
│   └── apps.json              ← Catálogo de apps (hospedado no GitHub)
│
├── scripts/
│   ├── windows/
│   │   ├── _template.bat      ← Template base para Windows
│   │   ├── install-devnotes.bat
│   │   ├── install-quickterm.bat
│   │   └── ...
│   ├── linux/
│   │   ├── _template.sh
│   │   ├── install-devnotes.sh
│   │   └── ...
│   └── macos/
│       ├── install-devnotes.sh
│       └── ...
│
└── apps/                      ← Pacotes dos apps (zip/tar.gz)
    ├── devnotes/
    │   ├── devnotes-windows.zip
    │   ├── devnotes-linux.tar.gz
    │   └── devnotes-macos.tar.gz
    └── ...
```

**Dados locais** (criados automaticamente em `~/.localstore/`):
```
~/.localstore/
├── installed.json      ← Histórico de apps instalados
├── catalog_cache.json  ← Cache do JSON do GitHub
└── localstore.log      ← Log de operações
```

---

## ➕ Como adicionar um novo app ao catálogo

Edite `data/apps.json` no seu repositório GitHub e adicione uma entrada ao array `apps`:

```json
{
  "id": "meuapp",
  "name": "MeuApp",
  "version": "1.0.0",
  "category": "Utilitários",
  "description": "Descrição do que o app faz.",
  "author": "Seu Nome",
  "icon": "🛠️",
  "tags": ["ferramenta", "util"],
  "size": "5MB",
  "downloads": {
    "windows": "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/apps/meuapp/meuapp-windows.zip",
    "linux":   "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/apps/meuapp/meuapp-linux.tar.gz",
    "macos":   "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/apps/meuapp/meuapp-macos.tar.gz"
  },
  "install_scripts": {
    "windows": "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/scripts/windows/install-meuapp.bat",
    "linux":   "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/scripts/linux/install-meuapp.sh",
    "macos":   "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/scripts/macos/install-meuapp.sh"
  },
  "dependencies": [],
  "changelog": {
    "1.0.0": "Lançamento inicial"
  },
  "homepage": "https://github.com/SEU_USUARIO/meuapp"
}
```

Depois:
1. Faça `git commit` e `git push` do JSON atualizado
2. Suba os arquivos do app (zip/tar.gz) na pasta `apps/meuapp/`
3. Suba os scripts de instalação em `scripts/windows/` e `scripts/linux/`
4. Usuários clicam em "↻ Atualizar" no LocalStore — o novo app aparece automaticamente

**Nenhuma alteração no código do LocalStore é necessária.**

---

## 🖥️ Scripts de instalação

### Windows (.bat)
- Execute como Administrador
- Copia arquivos para `C:\Program Files\NomeDoApp\`
- Cria atalho na Área de Trabalho
- Registra no Painel de Controle > Programas

### Linux (.sh)
- Execute com `sudo`
- Instala em `/opt/nomeapp/`
- Cria link simbólico em `/usr/local/bin/`
- Cria entrada `.desktop` para o menu

### macOS (.sh)
- Cria bundle `.app` em `/Applications/`
- Registra no Launch Services
- Cria link de linha de comando em `/usr/local/bin/`

---

## 🔄 Fluxo de instalação

```
Usuário clica "Instalar"
        ↓
LocalStore baixa o pacote (zip/tar.gz) do GitHub
        ↓
Extrai em pasta temporária (~tmp/localstore_NomeApp/)
        ↓
Baixa o script de instalação correspondente ao OS
        ↓
Executa o script (sudo/admin conforme necessário)
        ↓
Registra em ~/.localstore/installed.json
        ↓
Limpa arquivos temporários
```

---

## 🏗️ Evoluções futuras sugeridas

| Feature | Como implementar |
|---|---|
| Assinatura criptográfica | Adicionar hash SHA256 no JSON, verificar antes de executar |
| Atualizações automáticas | Checar versão no startup e notificar |
| Desinstalação integrada | Incluir `uninstall.bat/sh` junto com o app |
| Múltiplos repositórios | Array de `CATALOG_URLS` no config |
| Interface Electron | Portar o Python para Node.js + HTML |
| Empacotamento `.exe` | Usar PyInstaller: `pyinstaller --onefile localstore.py` |
| Auto-elevação de permissões | Adicionar UAC prompt no Windows, pkexec no Linux |
