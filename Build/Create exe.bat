@echo off
python -m PyInstaller --noconfirm --windowed --onefile --noupx --uac-admin --distpath . --icon Rme.ico --collect-all customtkinter --collect-all psutil re4_master_editor.py
pause
