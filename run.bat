@echo off
echo ========================================
echo   Starting HCL Copilot...
echo ========================================

cd /d %~dp0

echo Checking GROQ API key...
if "%GROQ_API_KEY%"=="" (
    echo.
    echo ERROR: GROQ_API_KEY is not set.
    echo Please set it using:
    echo setx GROQ_API_KEY "your_key_here"
    echo Then restart your computer.
    pause
    exit
)

echo.
echo Starting Streamlit App...
echo.

py -m streamlit run app.py

pause
