from app.adapters.base import BaseFAIRToolAdapter
from app.adapters.http_client import FAIRToolHTTPClient
from app.models.fair_result import FAIRToolResult
from app.schemas.compare import PrincipleScores
from app.schemas.metadata import DatasetMetadata


class FAIRCheckerAdapter(BaseFAIRToolAdapter):
    def __init__(
        self,
        http_client: FAIRToolHTTPClient | None = None,
        base_url: str = "https://fair-checker.france-bioinformatique.fr/api/check",
    ) -> None:
        self.http_client = http_client or FAIRToolHTTPClient()
        self.base_url = base_url

    def assess(self, metadata: DatasetMetadata) -> FAIRToolResult:
        payload = self.http_client.get_json(
            self.base_url,
            params={"url": metadata.identifier},
        )

        return FAIRToolResult(
            tool_name="fair-checker",
            overall_score=self._extract_overall_score(payload),
            principle_scores=PrincipleScores(
                findable=self._extract_principle_score(payload, "findable"),
                accessible=self._extract_principle_score(payload, "accessible"),
                interoperable=self._extract_principle_score(payload, "interoperable"),
                reusable=self._extract_principle_score(payload, "reusable"),
            ),
            raw_summary="Real assessment from FAIR-Checker.",
            notes=self._extract_notes(payload),
        )

    def _extract_overall_score(self, payload: dict) -> float:
        score = payload.get("overall_score", 0)
        return round(float(score), 2)

    def _extract_principle_score(self, payload: dict, key: str) -> float:
        principles = payload.get("principles", {})
        score = principles.get(key, 0)
        return round(float(score), 2)

    def _extract_notes(self, payload: dict) -> list[str]:
        notes: list[str] = []
        checks = payload.get("checks", [])
        for item in checks[:5]:
            name = item.get("name")
            status = item.get("status")
            if name and status:
                notes.append(f"{name}: {status}")
        return notes