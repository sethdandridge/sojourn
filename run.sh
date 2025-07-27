#source env.sh
#flask run --host="0.0.0.0" --port=5000

gunicorn -w 10 -b 0.0.0.0:80 --preload "app:create_app()"
