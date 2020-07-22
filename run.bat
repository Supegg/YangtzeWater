@echo off

cd /d %~dp0
call venv\\Scripts\\activate

python water.py >> log.txt 2>&1

deactivate
exit