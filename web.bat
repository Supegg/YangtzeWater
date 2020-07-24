@echo off

cd /d %~dp0
call venv\\Scripts\\activate

echo "web server at http://0.0.0.0:8001/"
python -m http.server --bind 0.0.0.0 8001 >> web.log 2>&1 

deactivate
exit
