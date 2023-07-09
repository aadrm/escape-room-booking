bind = '127.0.0.1:8000'  # Specify the IP address and port to bind Gunicorn to
workers = 2  # Number of worker processes to handle incoming requests
loglevel = 'info'  # Log level (options: debug, info, warning, error, critical)
errorlog = '-'  # Specify the error log file ('-' means log to stdout)
accesslog = '-'  # Specify the access log file ('-' means log to stdout)
