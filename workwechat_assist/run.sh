# 启动gunicorn
gunicorn config.wsgi:application -c gunicorn.py > ./logs/gunicorn.log 2>&1 &


# celery worker
# celery multi start djWorker -A config.celery_app -l info -f ./logs/djWorker.log --pidfile=./logs/djWorker.pid
#   celery multi stop djWorker -A config.celery_app -l info -f ./logs/djWorker.log --pidfile=./logs/djWorker.pid

# celery beat
# celery -A config.celery_app beat -l info -f ./logs/djBeat.log --pidfile=./logs/djBeat.pid  --detach

# flower
#celery -A config.celery_app flower --port=5555

