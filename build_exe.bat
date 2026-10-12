@echo off
title Build LinesOfCodeCounter EXE
cd /d "%~dp0"
python code_counter_gui.py --build
pause
