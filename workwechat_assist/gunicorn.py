import os
import environ
import multiprocessing
bind = '0.0.0.0:9090'
timeout = 30 #超时
#worker_class = 'gevent'
workers = multiprocessing.cpu_count()
reload = True
daemon = True

root_dir = environ.Path(__file__)-1

loglevel = 'debug'
errorlog = '{}/logs/gunicorn.err.log'.format(root_dir)
accesslog = '{}/logs/gunicorn.access.log'.format(root_dir)
proc_name = 'gunicorn_WorkWechatAssist'
