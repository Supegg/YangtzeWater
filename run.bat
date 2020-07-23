@echo off

cd /d %~dp0
call venv\\Scripts\\activate

python water.py 2 >> log.txt 2>&1

deactivate
exit