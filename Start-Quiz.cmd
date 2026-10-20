@echo off
setlocal
cd /d "%~dp0"
if exist "%LOCALAPPDATA%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" goto bundled_local
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" goto bundled_user
where py >nul 2>nul
if not errorlevel 1 goto use_py
where python >nul 2>nul
if not errorlevel 1 goto use_python
echo Python 3.9 eller nyere skal installeres for at starte Quizklubben.
pause
exit /b 1
:bundled_local
"%LOCALAPPDATA%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" server.py
goto done
:bundled_user
"%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" server.py
goto done
:use_py
py -3 server.py
goto done
:use_python
python server.py
:done
if errorlevel 1 pause
endlocal
