@echo off
REM Запуск игры из каталога этого файла. Удобно привязать ярлык к этому .bat
pushd "%~dp0"

REM если есть pythonw в PATH — используем его, чтобы не показывать консоль
where pythonw >nul 2>&1
if %ERRORLEVEL%==0 (
    pythonw "%~dp0main.py"
) else (
    REM fallback на python (покажет консоль)
    python "%~dp0main.py"
)

popd
exit /b
