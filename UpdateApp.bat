@echo off
color 0A
echo ------------------------------------------
echo   BE-SECURE HARDWARE - ADMIN PANEL
echo ------------------------------------------
echo.
echo 1. Processing Excel Data...
python process_data.py

echo.
echo 2. Uploading to Online Database (GitHub)...
git add .
git commit -m "Admin update: Rates updated"
git push origin master

echo.
echo ------------------------------------------
echo   SUCCESS! App is now updated for Dealers.
echo ------------------------------------------
pause