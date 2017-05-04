# -*- coding: utf-8 -*-
"""This module is used to reload the modules automatically when any changes is
detected. Only use for development"""

import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

process = None


def log(s):
    print('[Monitor] %s' % s)


class Monitor(FileSystemEventHandler):
    def __init__(self, func):
        super(Monitor, self).__init__()
        self.restart = func

    def on_any_event(self, event):
        """
        The original method on_any_event in class FileSystemEventHandler is
        empty. There is a completement.
        """
        if event.src_path.endswith('.py'):
            log('Python source file changed: %s' % event.src_path)
            self.restart()


def kill_process():
    global process
    if process:
        log('killing process [%s]...' % process.pid)
        process.kill()
        process.wait()
        process = None


def start_process():
    global process, command
    log('start process %s...' % ' '.join(command))
    process = subprocess.Popen(
        command,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )


def restart_process():
    kill_process()
    start_process()


def start_watch(path, callback):
    observer = Observer()
    observer.schedule(Monitor(restart_process), path, recursive=True)
    observer.start()
    log('Watching directory %s...' % path)
    start_process()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        print('Usage: autoreload.py your-script.py')
        exit(0)
    if argv[0] != 'python3':
        argv.insert(0, 'python3')
    command = argv
    path = os.path.abspath('.')  # use the same directory path
    start_watch(path, None)
