@echo off
:start
echo ========================================
echo    SISTEM PAKAR DIAGNOSA MEDIS
echo ========================================
echo.
echo Pilih mode aplikasi:
echo 1. Web Mode (Recommended) - Browser Interface
echo 2. Desktop GUI Mode (Tkinter Interface)
echo 3. CLI Mode (Command Line Interface) 
echo 4. Launcher GUI (All Options)
echo 5. Run Tests
echo 6. Exit
echo.

set /p choice="Masukkan pilihan (1-6): "

if "%choice%"=="1" (
    echo.
    echo Memulai Web Mode...
    echo Buka browser dan akses: http://localhost:5000
    echo Press Ctrl+C to stop the server
    echo.
    cd web_ui
    "C:/Users/rdest/OneDrive/Documents/SISPAK 2/.venv/Scripts/python.exe" app.py
) else if "%choice%"=="2" (
    echo.
    echo Memulai Desktop GUI Mode...
    "C:/Users/rdest/OneDrive/Documents/SISPAK 2/.venv/Scripts/python.exe" main.py
) else if "%choice%"=="3" (
    echo.
    echo Memulai CLI Mode...
    "C:/Users/rdest/OneDrive/Documents/SISPAK 2/.venv/Scripts/python.exe" cli.py
) else if "%choice%"=="4" (
    echo.
    echo Memulai Launcher GUI...
    "C:/Users/rdest/OneDrive/Documents/SISPAK 2/.venv/Scripts/python.exe" launcher.py
) else if "%choice%"=="5" (
    echo.
    echo Menjalankan Tests...
    "C:/Users/rdest/OneDrive/Documents/SISPAK 2/.venv/Scripts/python.exe" test_system.py
) else if "%choice%"=="6" (
    echo.
    echo Terima kasih!
    exit
) else (
    echo.
    echo Pilihan tidak valid!
    pause
    goto start
)

echo.
pause
goto start