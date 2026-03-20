@echo off
:: ============================================================
:: Template genérico de instalação — Windows
:: Usado como base para todos os apps do LocalStore
:: ============================================================
:: Variáveis injetadas pelo LocalStore:
::   APP_NAME, APP_VERSION, EXTRACTED_DIR
:: ============================================================
setlocal EnableDelayedExpansion

:: ── Configuração do app ──────────────────────────────────────
set APP_NAME=NomeDoApp
set APP_VERSION=1.0.0
set APP_EXE=app.exe
set INSTALL_BASE=C:\Program Files
set INSTALL_DIR=%INSTALL_BASE%\%APP_NAME%

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║   LocalStore — Instalando %APP_NAME%
echo  ╚══════════════════════════════════════════════╝
echo.

:: Verificar admin
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Necessário executar como Administrador.
    pause & exit /b 1
)

:: 1. Instalar
echo [1/4] Criando diretório de instalação...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [2/4] Copiando arquivos...
xcopy /E /I /Y "%~dp0extracted\*" "%INSTALL_DIR%\" >nul 2>&1
if not exist "%INSTALL_DIR%\%APP_EXE%" (
    echo [AVISO] Executável não encontrado, criando placeholder...
    echo @echo off > "%INSTALL_DIR%\%APP_EXE%"
    echo echo %APP_NAME% v%APP_VERSION% & pause >> "%INSTALL_DIR%\%APP_EXE%"
)

:: 2. Atalho área de trabalho
echo [3/4] Criando atalho...
set LNK=%PUBLIC%\Desktop\%APP_NAME%.lnk
powershell -NoProfile -Command ^
  "$s=(New-Object -COM WScript.Shell).CreateShortcut('%LNK%'); ^
   $s.TargetPath='%INSTALL_DIR%\%APP_EXE%'; ^
   $s.WorkingDirectory='%INSTALL_DIR%'; ^
   $s.Description='%APP_NAME% v%APP_VERSION%'; ^
   $s.Save()"

:: 3. Registro Windows (uninstall)
echo [4/4] Registrando no sistema...
set REG_PATH=HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%
reg add "%REG_PATH%" /v DisplayName       /t REG_SZ /d "%APP_NAME%"       /f >nul
reg add "%REG_PATH%" /v DisplayVersion    /t REG_SZ /d "%APP_VERSION%"    /f >nul
reg add "%REG_PATH%" /v InstallLocation   /t REG_SZ /d "%INSTALL_DIR%"    /f >nul
reg add "%REG_PATH%" /v Publisher         /t REG_SZ /d "LocalStore"       /f >nul
reg add "%REG_PATH%" /v UninstallString   /t REG_SZ /d "rmdir /s /q \"%INSTALL_DIR%\"" /f >nul

echo.
echo  ✅  %APP_NAME% v%APP_VERSION% instalado com sucesso!
echo      Local: %INSTALL_DIR%
echo.
exit /b 0
