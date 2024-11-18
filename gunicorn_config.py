bind = "0.0.0.0:8000"
workers = 3  # Adjust the number of workers based on your needs
worker_class = "sync"  # You can change this to "gevent" or "eventlet" if needed
timeout = 30  # Timeout for workers
loglevel = "info"  # Logging level
accesslog = "./access.log"  # Log to stdout
errorlog = "./error.log"  # Log to stderr