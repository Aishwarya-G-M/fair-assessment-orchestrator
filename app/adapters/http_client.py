import httpx


class FAIRToolHTTPClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    def get_json(
        self,
        url: str,
        params: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
    ) -> dict:
        response = httpx.get(
            url,
            params=params,
            auth=auth,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def post_json(
        self,
        url: str,
        json_body: dict,
        auth: tuple[str, str] | None = None,
    ) -> dict:
        response = httpx.post(
            url,
            json=json_body,
            auth=auth,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()