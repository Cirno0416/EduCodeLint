from frontend.services.api_client import ApiClient


class RecordController:
    def __init__(self):
        self.api = ApiClient()

    def get_records(self, page, page_size):
        return self.api.get_records(page, page_size)

    def get_analysis_detail(self, analysis_id):
        return self.api.get_analysis_detail(analysis_id)

    def delete_record(self, analysis_id):
        """删除指定记录"""
        return self.api.delete_record(analysis_id)
