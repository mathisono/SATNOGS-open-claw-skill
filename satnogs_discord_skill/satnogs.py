"""Small SatNOGS Network API client using only the Python standard library."""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Any, Iterator, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .timeutils import api_datetime


class SatnogsApiError(RuntimeError):
    """Raised when the SatNOGS Network API request fails."""


class SatnogsClient:
    """Read-only client for SatNOGS Network observations."""

    def __init__(self, base_url: str = "https://network.satnogs.org", *, token: Optional[str] = None, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "SATNOGS-open-claw-skill/0.1 (+https://github.com/mathisono/SATNOGS-open-claw-skill)",
        }
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers

    def _url(self, path_or_url: str, params: Optional[Mapping[str, Any]] = None) -> str:
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            base = path_or_url
        else:
            base = f"{self.base_url}/{path_or_url.lstrip('/')}"
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        if clean_params:
            separator = "&" if "?" in base else "?"
            return f"{base}{separator}{urlencode(clean_params)}"
        return base

    def get_json(self, path_or_url: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        """GET a JSON document, retrying once when the API returns 429."""

        url = self._url(path_or_url, params)
        request = Request(url, headers=self._headers(), method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = min(300, max(1, int(retry_after or "60")))
                except ValueError:
                    delay = 60
                time.sleep(delay)
                try:
                    with urlopen(request, timeout=self.timeout) as response:
                        return json.loads(response.read().decode("utf-8"))
                except (HTTPError, URLError, json.JSONDecodeError) as retry_exc:
                    raise SatnogsApiError(f"SatNOGS API retry failed for {url}: {retry_exc}") from retry_exc
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                body = ""
            raise SatnogsApiError(f"SatNOGS API HTTP {exc.code} for {url}: {body}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise SatnogsApiError(f"SatNOGS API request failed for {url}: {exc}") from exc

    def iter_pages(self, path: str, params: Mapping[str, Any]) -> Iterator[dict[str, Any]]:
        """Yield items from DRF-style or list-plus-Link-header pagination."""

        next_url: Optional[str] = path
        next_params: Optional[Mapping[str, Any]] = params
        while next_url:
            data = self.get_json(next_url, next_params)
            next_params = None
            if isinstance(data, dict) and "results" in data:
                for item in data.get("results") or []:
                    if isinstance(item, dict):
                        yield item
                next_url = data.get("next")
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        yield item
                next_url = None
            elif isinstance(data, dict):
                yield data
                next_url = None
            else:
                next_url = None

    def list_future_observations(
        self,
        *,
        station_id: int,
        start: datetime,
        end_before: datetime,
        max_results: int = 100,
    ) -> list[dict[str, Any]]:
        params = {
            "ground_station": station_id,
            "status": "future",
            "start": api_datetime(start),
            "start__lt": api_datetime(end_before),
        }
        observations: list[dict[str, Any]] = []
        for obs in self.iter_pages("/api/observations/", params):
            observations.append(obs)
            if len(observations) >= max_results:
                break
        return sorted(observations, key=lambda item: str(item.get("start") or ""))

    def get_observation(self, observation_id: int | str) -> dict[str, Any]:
        data = self.get_json(f"/api/observations/{observation_id}/")
        if not isinstance(data, dict):
            raise SatnogsApiError(f"Observation {observation_id} response was not an object")
        return data


def observation_page_url(api_base_url: str, observation_id: int | str) -> str:
    """Return the human-readable SatNOGS Network observation page URL."""

    base = api_base_url.rstrip("/")
    return f"{base}/observations/{observation_id}/"
