import requests

from frontend.config.settings import BASE_URL


class ApiClient:
    def analyze_single(self, path, exclude_tools):
        return requests.post(
            f"{BASE_URL}/analyze/single",
            json={"path": path, "exclude_tools": exclude_tools}
        ).json()

    def analyze_multiple(self, paths, exclude_tools):
        return requests.post(
            f"{BASE_URL}/analyze/multiple",
            json={"paths": paths, "exclude_tools": exclude_tools}
        ).json()

    def get_records(self, page, page_size):
        return requests.get(
            f"{BASE_URL}/records",
            params={
                "page": page,
                "page_size": page_size
            }
        ).json()

    def get_analysis_detail(self, analysis_id):
        return requests.get(
            f"{BASE_URL}/records/analysis",
            params={
                "analysis_id": analysis_id
            }
        ).json()

    def delete_record(self, analysis_id):
        return requests.delete(
            f"{BASE_URL}/records/delete",
            params={
                "analysis_id": analysis_id
            }
        ).json()

    def compare(self, analysis_id_1, analysis_id_2):
        return requests.post(
            f"{BASE_URL}/compare",
            json={
                "analysis_id_1": analysis_id_1,
                "analysis_id_2": analysis_id_2
            }
        ).json()
