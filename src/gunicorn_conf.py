# Gunicorn config variables
loglevel = 'warning'
errorlog = "-"  # stderr
accesslog = "-"  # stdout
worker_tmp_dir = "/dev/shm"
graceful_timeout = 30
timeout = 30
keepalive = 5
threads = 4
