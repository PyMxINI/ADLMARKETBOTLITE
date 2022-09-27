@echo off
title ADLMARKETBOTLITE
:loop
python main.py
timeout /t 60
goto loop
