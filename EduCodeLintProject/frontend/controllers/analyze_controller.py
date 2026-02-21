from frontend.services.api_client import ApiClient


class AnalyzeController:
    def __init__(self):
        self.api = ApiClient()

    def analyze(self, files, exclude_tools):
        if len(files) == 1:
            return self.api.analyze_single(files[0], exclude_tools)
        return self.api.analyze_multiple(files, exclude_tools)
