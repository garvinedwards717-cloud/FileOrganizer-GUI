from pathlib import Path
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from organizer import organize_new_file


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if event.is_directory:
            return

        time.sleep(1)

        try:
            result = organize_new_file(event.src_path)
            self.callback(result)
        except Exception as error:
            self.callback(f"Watch error: {error}")


class FolderWatcher:
    def __init__(self, folder_path: str, callback):
        self.folder_path = Path(folder_path)
        self.callback = callback
        self.observer = Observer()

    def start(self):
        event_handler = NewFileHandler(self.callback)
        self.observer.schedule(event_handler, str(self.folder_path), recursive=False)
        self.observer.start()

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()