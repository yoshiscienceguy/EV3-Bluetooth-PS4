pip install -r requirements.txt
set FLASK_APP=app
set FLASK_ENV=development
set FLASK_DEBUG=True
set FLASK_RUN_PORT=8040
start chrome "http://127.0.0.1:8040/"
python -m flask run
