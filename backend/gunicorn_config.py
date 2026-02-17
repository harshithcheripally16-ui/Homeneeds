# backend/gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 2
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
