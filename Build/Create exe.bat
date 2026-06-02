@echo off
python -m PyInstaller --noconfirm --windowed --uac-admin --distpath dist --icon Rme.ico --collect-all customtkinter --collect-all psutil re4_master_editor.py
pause
