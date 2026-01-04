from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/home/budt748s04t03/flaskapp/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/budt748s04t03/flaskapp/access_log'
errorlog =  '/home/budt748s04t03/flaskapp/error_log'
