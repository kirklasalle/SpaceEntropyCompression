"""Gunicorn production WSGI server configuration for EMRF service."""

import multiprocessing

bind = "0.0.0.0:5000"
workers = max(2, min(multiprocessing.cpu_count(), 4))
threads = 2
worker_class = "gthread"
timeout = 120
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"
