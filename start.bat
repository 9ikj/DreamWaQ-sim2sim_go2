@echo off
set PYTHONPATH=%~dp0
call conda run -n go2 python scripts/dreamwaq_go2.py