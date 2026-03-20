@echo off
:: ============================================================
:: Script de Instalação - DevNotes v2.1.0
:: Gerado pelo LocalStore
:: ============================================================
setlocal EnableDelayedExpansion

set APP_NAME=DevNotes
set APP_VERSION=2.1.0
set INSTALL_DIR=C:\Program Files\%APP_NAME%
set TEMP_DIR=%TEMP%\localstore_%APP_NAME%

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   Instalando %APP_NAME% v%APP_VERSION%          ║
echo  ╚══════════════════════════════════════╝
echo.

:: Verificar permissões de administrador
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [ERRO] Este instalador precisa de permissões de Administrador.
    echo        Clique com botão direito e escolha "Executar como administrador".
    pause
    exit /b 1
)

:: Criar pasta temporária
echo [1/5] Preparando instalação...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

:: Criar pasta de instalação
echo [2/5] Criando diretório em %INSTALL_DIR%...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Simular cópia de arquivos (em produção, o arquivo já estará extraído pelo LocalStore)
echo [3/5] Copiando arquivos do %APP_NAME%...

:: Criar executável fictício para demonstração
echo @echo off > "%INSTALL_DIR%\%APP_NAME%.exe"
echo echo %APP_NAME% v%APP_VERSION% iniciado! >> "%INSTALL_DIR%\%APP_NAME%.exe"
echo pause >> "%INSTALL_DIR%\%APP_NAME%.exe"

:: Criar arquivo de configuração padrão
echo { > "%INSTALL_DIR%\config.json"
echo   "version": "%APP_VERSION%", >> "%INSTALL_DIR%\config.json"
echo   "theme": "dark", >> "%INSTALL_DIR%\config.json"
echo   "font_size": 14, >> "%INSTALL_DIR%\config.json"
echo   "auto_save": true >> "%INSTALL_DIR%\config.json"
echo } >> "%INSTALL_DIR%\config.json"

:: Criar atalho na área de trabalho
echo [4/5] Criando atalhos...
set SHORTCUT=%USERPROFILE%\Desktop\%APP_NAME%.lnk
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%INSTALL_DIR%\%APP_NAME%.exe'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.Save()"

:: Registrar no registro do Windows (para desinstalação)
echo [5/5] Registrando instalação...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayName" /t REG_SZ /d "%APP_NAME%" /f >nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayVersion" /t REG_SZ /d "%APP_VERSION%" /f >nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "Publisher" /t REG_SZ /d "LocalStore" /f >nul

:: Limpeza
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"

echo.
echo  ✓ %APP_NAME% instalado com sucesso em:
echo    %INSTALL_DIR%
echo.
echo  Atalho criado na área de trabalho.
echo.
pause
exit /b 0
