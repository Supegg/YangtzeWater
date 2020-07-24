@echo on

cd /d %~dp0
call venv\\Scripts\\activate

python water.py 2 >> run.log 2>&1

git add .
git commit -m "more datas, auto commit"
git push

deactivate

exit
