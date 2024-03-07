import subprocess
import sys
import os
import signal
import psutil
import logging
logger = logging.getLogger(__name__)

PID_FILE = 'app.pid'

def start_app():
    python_interpreter = os.path.join(os.path.dirname(sys.executable), 'python')
    process = subprocess.Popen([python_interpreter, "app.py"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    logger.info(f"App started with PID: {process.pid}")
    with open(PID_FILE, 'w') as f:
        f.write(str(process.pid))

def stop_app():
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read())
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):  # or parent.children() for recursive=False
            child.kill()
        parent.kill()
        logger.info(f"App stopped with PID: {pid}")
        os.remove(PID_FILE)
    except FileNotFoundError:
        logger.info("App is not running")

def restart_app():
    stop_app()
    start_app()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.info("Usage: python cli.py {start|stop|restart}")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        start_app()
    elif command == "stop":
        stop_app()
    elif command == "restart":
        restart_app()
    else:
        logger.info(f"Unknown command: {command}")
        sys.exit(1)