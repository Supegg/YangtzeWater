#!/bin/bash

work_path=$(dirname $0)
cd ./${work_path} 

source ./venv/bin/activate
echo "web server at http://0.0.0.0:8001/"
python -m http.server --bind 0.0.0.0 8001 >> web.log 2>&1 &

exit
