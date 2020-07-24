#!/bin/bash

work_path=$(dirname $0)
cd ./${work_path} 

source ./venv/bin/activate

python ./water.py 2 >> run.log 2>&1

git add .
git commit -m "more datas, auto commit"
git push

deactivate

exit
