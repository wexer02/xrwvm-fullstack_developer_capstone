"""Run the capstone's private services and public Django server in the course container."""
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import time
from urllib.request import urlopen

root = Path(__file__).resolve().parent
os.chdir(root)
os.environ.setdefault('DJANGO_SECRET_KEY', secrets.token_urlsafe(48))
os.environ.setdefault('INTERNAL_API_KEY', secrets.token_urlsafe(32))
os.environ.setdefault('DATABASE_PATH', '/data/db.sqlite3')
Path('/data/mongo').mkdir(parents=True, exist_ok=True)
children = []


def stop(signum=None, frame=None):
    for child in reversed(children):
        child.terminate()
    for child in children:
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
    sys.exit(0 if signum else 1)


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)


def start(command):
    process = subprocess.Popen(command)
    children.append(process)


def ready(url):
    for _ in range(90):
        if any(child.poll() is not None for child in children):
            raise RuntimeError('A service exited during startup.')
        try:
            with urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(1)
    raise RuntimeError('Service did not become ready: ' + url)


try:
    # shortcut: one course container; use managed databases and separate deployments for production.
    start(['mongod', '--dbpath', '/data/mongo', '--bind_ip', '127.0.0.1',
           '--wiredTigerCacheSizeGB', '0.25', '--logpath', '/tmp/mongo.log'])
    start(['node', 'database/app.js'])
    start([sys.executable, '-m', 'gunicorn', '--bind', '127.0.0.1:5050',
           '--workers', '1', 'djangoapp.microservices.app:app'])
    ready('http://127.0.0.1:3030/')
    ready('http://127.0.0.1:5050/')
    for arguments in [('migrate', '--noinput'), ('seed_cars',), ('collectstatic', '--noinput')]:
        subprocess.run([sys.executable, 'manage.py', *arguments], check=True)
    start([sys.executable, '-m', 'gunicorn', '--bind', '0.0.0.0:' + os.getenv('PORT', '8000'),
           '--workers', '2', '--access-logfile', '-', 'djangoproj.wsgi:application'])
    while all(child.poll() is None for child in children):
        time.sleep(1)
finally:
    stop()
