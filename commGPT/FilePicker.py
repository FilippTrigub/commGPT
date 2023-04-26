import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            global new_file_path
            new_file_path = event.src_path
            FilePicker.PICKED_FILE_PATH = new_file_path


class FilePicker:
    WATCH_PATH = None
    PICKED_FILE_PATH = None
    WATCHING = False

    def __init__(self, watch_path='recorder_output'):
        self.WATCH_PATH = watch_path
    def toggle_watching(self):
        self.WATCHING = not self.WATCHING

    def watch_continuous(self):

        self.watch_directory()

        while self.WATCHING:
            new_file_path = self.get_new_file_path()
            if new_file_path:
                print(f'New file created: {new_file_path}')
            time.sleep(1)

    def watch_directory(self):
        global new_file_path
        new_file_path = None
        event_handler = NewFileHandler()
        observer = Observer()
        observer.schedule(event_handler, self.WATCH_PATH, recursive=False)
        observer.start()
        try:
            while self.WATCHING:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def get_new_file_path(self):
        global previous_file_path
        new_file_path = None
        while not new_file_path:
            self.watch_directory()
            if new_file_path != previous_file_path:
                previous_file_path = new_file_path
                return new_file_path
            else:
                new_file_path = None
