from PyQt6.QtCore import QObject, pyqtSignal


class RecordWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, controller, page, page_size):
        super().__init__()
        self.controller = controller
        self.page = page
        self.page_size = page_size

    def run(self):
        try:
            result = self.controller.get_records(
                self.page,
                self.page_size
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
