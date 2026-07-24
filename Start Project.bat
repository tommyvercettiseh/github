@echo off
setlocal
cd /d "%~dp0"
title GitHub Hub

if not exist logs mkdir logs

echo [1/3] Python controleren...
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo [FOUT] Python is niet gevonden.
    echo Installeer Python 3.11 of nieuwer en vink Add Python to PATH aan.
    start "" "https://www.python.org/downloads/windows/"
    pause
    exit /b 1
)

echo [2/3] Git controleren...
where git >nul 2>&1
if errorlevel 1 (
    echo.
    echo [FOUT] Git is niet gevonden.
    start "" "https://git-scm.com/download/win"
    pause
    exit /b 1
)

echo [3/3] GitHub CLI controleren...
where gh >nul 2>&1
if errorlevel 1 (
    echo.
    echo [LET OP] GitHub CLI ontbreekt.
    echo De downloadpagina wordt geopend. Installeer GitHub CLI en start daarna opnieuw.
    start "" "https://cli.github.com/"
    pause
    exit /b 1
)

echo GitHub Hub starten...
python app.py >> logs\launcher.log 2>&1

if errorlevel 1 (
    echo.
    echo [FOUT] De app kon niet worden gestart.
    echo Bekijk logs\launcher.log voor details.
    pause
)

endlocal
