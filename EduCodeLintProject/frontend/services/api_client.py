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
