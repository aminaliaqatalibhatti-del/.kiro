@echo off
echo Clearing Python cache...
for /d /r "C:\Users\angry\OneDrive\Desktop\rabia\backend\backend" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)
del /s /q "C:\Users\angry\OneDrive\Desktop\rabia\backend\backend\*.pyc" 2>nul
echo Cache cleared.
echo Starting TripPilot AI server...
cd /d "C:\Users\angry\OneDrive\Desktop\rabia\backend\backend"
python app.py
