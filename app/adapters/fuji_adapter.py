import os
from typing import Any

import httpx

from app.adapters.base import BaseFAIRToolAdapter
from app.adapters.http_client import FAIRToolHTTPClient
from app.schemas.compare import PrincipleScores, ToolResult
from app.schemas.metadata import DatasetMetadata


class FUJIAdapter(BaseFAIRToolAdapter):
    def __init__(
        self,
        http_client: FAIRToolHTTPClient | None = None,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self.http_client = http_client or FAIRToolHTTPClient()
        self.base_url = (
            base_url
            or os.getenv("FUJI_BASE_URL")
            or "http://localhost:1071/fuji/api/v1/evaluate"
        )
        self.username = username or os.getenv("FUJI_USERNAME")
        self.password = password or os.getenv("FUJI_PASSWORD")

    def assess(self, metadata: DatasetMetadata) -> ToolResult:
        auth = None
        if self.username and self.password:
            auth = (self.username, self.password)

        try:
            payload = self.http_client.post_json(
                url=self.base_url,
                json_body={
                    "object_identifier": metadata.identifier,
                    "test_debug": False,
                },
                auth=auth,
            )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"F-UJI request failed: {exc}") from exc

        summary = payload.get("summary", {})
        results = payload.get("results", [])
        resolved_url = payload.get("resolved_url") or metadata.identifier
        metric_version = payload.get("metric_version")
        software_version = payload.get("software_version")

        notes = self._extract_notes(results)
        if metric_version:
            notes.append(f"metric_version: {metric_version}")
        if software_version:
            notes.append(f"software_version: {software_version}")

        return ToolResult(
            tool_name="f-uji",
            overall_score=self._extract_overall_score(summary),
            principle_scores=PrincipleScores(
                findable=self._extract_principle_score(summary, "F"),
                accessible=self._extract_principle_score(summary, "A"),
                interoperable=self._extract_principle_score(summary, "I"),
                reusable=self._extract_principle_score(summary, "R"),
            ),
            raw_summary=f"F-UJI assessed resource {resolved_url}.",
            notes=notes,
        )

    def _extract_overall_score(self, summary: dict[str, Any]) -> float:
        if "score_percent" in summary:
            return round(float(summary["score_percent"]) / 100, 2)

        score = summary.get("score")
        return self._score_ratio(score)

    def _extract_principle_score(
        self,
        summary: dict[str, Any],
        principle: str,
    ) -> float:
        fair_percentage = summary.get("fair_percentage_by_principle", {})
        if principle in fair_percentage:
            return round(float(fair_percentage[principle]) / 100, 2)

        score_by_principle = summary.get("score_by_principle", {})
        if principle in score_by_principle:
            return self._score_ratio(score_by_principle[principle])

        return 0.0

    def _score_ratio(self, score_obj: Any) -> float:
        if not isinstance(score_obj, dict):
            return 0.0

        earned = float(score_obj.get("earned", 0))
        total = float(score_obj.get("total", 0))

        if total == 0:
            return 0.0

        return round(earned / total, 2)

    def _extract_notes(self, results: list[Any]) -> list[str]:
        notes: list[str] = []

        for item in results[:5]:
            if not isinstance(item, dict):
                continue

            metric_identifier = item.get("metric_identifier") or item.get("id")
            metric_name = item.get("metric_name") or item.get("name")
            status = item.get("test_status") or item.get("status")

            parts = [part for part in [metric_identifier, metric_name, status] if part]
            if parts:
                notes.append(": ".join(parts))

        return notes