@echo off
title Install Python Libraries

echo Updating pip...
python -m pip install --upgrade pip

echo.
echo Installing CustomTkinter (CTK)...
pip install customtkinter

echo.
echo Installing Psutil (PUSTIL)...
pip install psutil

echo.
echo Installing TkinterDnD2 (TINKERTDR2)...
pip install tkinterdnd2

echo.
echo Installation process completed.
pause
