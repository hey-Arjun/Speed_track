import threading
from action.api import send_event
from queue import Queue

metadata_queue = Queue()

def action_worker():
    while True:
        event = metadata_queue.get()
        if event is None: break
        send_event(event)
        metadata_queue.task_done()

threading.Thread(target=action_worker, daemon=True).start()
