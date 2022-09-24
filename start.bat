@echo off
title ADLMARKETBOTLITE
:loop
python main.py
timeout /t 5
goto loop
