from PyQt6.QtCore import QObject, pyqtSignal


class AnalyzeWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, controller, files, exclude_tools):
        super().__init__()
        self.controller = controller
        self.files = files
        self.exclude_tools = exclude_tools

    def run(self):
        try:
            result = self.controller.analyze(self.files, self.exclude_tools)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
