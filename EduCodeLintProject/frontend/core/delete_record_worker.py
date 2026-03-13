from PyQt6.QtCore import QObject, pyqtSignal


class DeleteRecordWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, controller, analysis_id):
        super().__init__()
        self.controller = controller
        self.analysis_id = analysis_id

    def run(self):
        try:
            result = self.controller.delete_record(self.analysis_id)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
