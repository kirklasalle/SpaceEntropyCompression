"""Gunicorn production WSGI server configuration for EMRF service."""

import multiprocessing
import os

bind = os.environ.get("EMRF_BIND", "127.0.0.1:5000")
workers = max(2, min(multiprocessing.cpu_count(), 4))
threads = 2
worker_class = "gthread"
# Exceeds _MAX_RUN_TIMEOUT_SEC (120s) so synchronous HTTP runs time out cleanly
# rather than being SIGKILLed mid-execution.
timeout = int(os.environ.get("EMRF_GUNICORN_TIMEOUT", "150"))
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"
