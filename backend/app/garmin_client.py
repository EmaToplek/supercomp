"""Small client for the Garmin Connect Personal API (owner's own account only)."""
import io
import zipfile
from datetime import date

import httpx

API_BASE = "https://personal.connectapi.garmin.com"
TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"
PAGE_SIZE = 100


class GarminError(Exception):
    pass


def extract_fit_from_zip(content: bytes) -> bytes:
    """Garmin sends the original file as a zip. Returns the .fit inside it."""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            for name in zip_file.namelist():
                if name.lower().endswith(".fit"):
                    return zip_file.read(name)
    except zipfile.BadZipFile:
        raise GarminError("Download is not a zip file")
    raise GarminError("No .fit file in the download")


class GarminClient:
    def __init__(self, api_key: str, timeout: float = 30):
        self._api_key = api_key
        self._http = httpx.Client(base_url=API_BASE, timeout=timeout)

    def close(self):
        self._http.close()

    def login(self):
        """Exchanges the personal API key for an access token (valid 24 h, no refresh)."""
        res = self._http.post(TOKEN_PATH, headers={"Authorization": f"ApiKey {self._api_key}"})
        self._check(res)
        token = res.text.strip()  
        if not token:
            raise GarminError("Empty token")
        self._http.headers["Authorization"] = f"Bearer {token}"

    def activities_since(self, start: date) -> list[dict]:
        """All activities from start until now, page by page."""
        activities = []
        offset = 0
        while True:
            res = self._http.get(
                "/activitylist-service/activities/search/activities",
                params={"start": offset, "limit": PAGE_SIZE, "startDate": start.isoformat()},
            )
            self._check(res)
            page = res.json()
            activities.extend(page)
            if len(page) < PAGE_SIZE:
                return activities
            offset += PAGE_SIZE

    def download_fit(self, activity_id: int) -> bytes:
        res = self._http.get(f"/download-service/files/activity/{activity_id}")
        self._check(res)
        return extract_fit_from_zip(res.content)

    @staticmethod
    def _check(res: httpx.Response):
        if res.status_code != 200:
            raise GarminError(f"{res.request.url.path} returned {res.status_code}")