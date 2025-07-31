@echo off
:: Script สำหรับรัน Demo GUI ปรับปรุง
:: Run Demo Script for Improved GUI

echo ========================================
echo    RC Beam Calculator - Improved GUI
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python ไม่พบ กรุณาติดตั้ง Python ก่อน
    pause
    exit /b 1
)

echo ✅ ตรวจพบ Python แล้ว

:: Check if required modules are installed
echo 🔍 ตรวจสอบ PyQt5...
python -c "import PyQt5; print('✅ PyQt5 พร้อมใช้งาน')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ PyQt5 ไม่พบ กรุณาติดตั้งก่อน
    echo 📦 รันคำสั่ง: py -m pip install PyQt5
    pause
    exit /b 1
)

echo 🔍 ตรวจสอบ matplotlib...
python -c "import matplotlib; print('✅ matplotlib พร้อมใช้งาน')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ matplotlib ไม่พบ กรุณาติดตั้งก่อน
    echo 📦 รันคำสั่ง: py -m pip install matplotlib
    pause
    exit /b 1
)

echo.
echo 🚀 เปิดโปรแกรม GUI ปรับปรุง...
echo.

:: Check if demo file exists
if not exist "demo_improved_gui.py" (
    echo ❌ ไฟล์ demo_improved_gui.py ไม่พบ
    pause
    exit /b 1
)

:: Run the improved GUI demo
python demo_improved_gui.py

echo.
echo 📋 โปรแกรมปิดแล้ว
echo 📖 ดูการเปรียบเทียบได้ที่ไฟล์ GUI_COMPARISON.md
echo.
pause
