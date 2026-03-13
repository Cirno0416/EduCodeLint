from frontend.services.api_client import ApiClient


class CompareController:
    def __init__(self):
        self.api = ApiClient()

    def compare(self, analysis_id_1, analysis_id_2):
        return self.api.compare(analysis_id_1, analysis_id_2)
