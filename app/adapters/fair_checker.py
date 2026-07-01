import json
from typing import Any

import httpx

from app.adapters.base import BaseFAIRToolAdapter
from app.adapters.http_client import FAIRToolHTTPClient
from app.schemas.compare import PrincipleScores, ToolResult
from app.schemas.metadata import DatasetMetadata


class FAIRCheckerAdapter(BaseFAIRToolAdapter):
    def __init__(
        self,
        http_client: FAIRToolHTTPClient | None = None,
        base_url: str = "https://fair-checker.france-bioinformatique.fr/api/check",
    ) -> None:
        self.http_client = http_client or FAIRToolHTTPClient()
        self.base_url = base_url

    def assess(self, metadata: DatasetMetadata) -> ToolResult:
        try:
            payload = self.http_client.get_json(
                self.base_url,
                params={"url": metadata.identifier},
            )
        except httpx.TimeoutException as exc:
            raise RuntimeError("FAIR-Checker request timed out") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"FAIR-Checker request failed: {exc}") from exc

        notes = self._extract_notes(payload)
        warnings: list[str] = []

        overall_score = self._extract_overall_score(payload, warnings)
        principle_scores = PrincipleScores(
            findable=self._extract_principle_score(payload, "findable", warnings),
            accessible=self._extract_principle_score(payload, "accessible", warnings),
            interoperable=self._extract_principle_score(payload, "interoperable", warnings),
            reusable=self._extract_principle_score(payload, "reusable", warnings),
        )

        llm_context = self._build_llm_context(
            metadata_identifier=metadata.identifier,
            payload=payload,
            notes=notes,
            warnings=warnings,
        )

        return ToolResult(
            tool_name="fair-checker",
            overall_score=overall_score,
            principle_scores=principle_scores,
            raw_summary="Assessment returned by FAIR-Checker.",
            notes=notes,
            raw_payload=payload,
            llm_context=llm_context,
            warnings=warnings,
            error=None,
        )

    def _extract_overall_score(
        self,
        payload: dict[str, Any],
        warnings: list[str],
    ) -> float | None:
        score = payload.get("overall_score")

        if isinstance(score, (int, float, str)):
            try:
                return round(float(score), 2)
            except (TypeError, ValueError):
                warnings.append("Could not parse FAIR-Checker overall_score as numeric.")
                return None

        warnings.append("FAIR-Checker overall_score was missing or not numeric.")
        return None

    def _extract_principle_score(
        self,
        payload: dict[str, Any],
        key: str,
        warnings: list[str],
    ) -> float | None:
        principles = payload.get("principles", {})
        if not isinstance(principles, dict):
            warnings.append("FAIR-Checker principles field was missing or not a dict.")
            return None

        score = principles.get(key)
        if isinstance(score, (int, float, str)):
            try:
                return round(float(score), 2)
            except (TypeError, ValueError):
                warnings.append(f"Could not parse FAIR-Checker principle score for {key}.")
                return None

        return None

    def _extract_notes(self, payload: dict[str, Any]) -> list[str]:
        notes: list[str] = []
        checks = payload.get("checks", [])
        if not isinstance(checks, list):
            return notes

        for item in checks[:5]:
            if not isinstance(item, dict):
                continue

            name = item.get("name")
            status = item.get("status")
            if name and status:
                notes.append(f"{name}: {status}")

        return notes

    def _build_llm_context(
        self,
        metadata_identifier: str,
        payload: dict[str, Any],
        notes: list[str],
        warnings: list[str],
    ) -> str:
        compact = {
            "tool": "fair-checker",
            "input_identifier": metadata_identifier,
            "notes": notes,
            "warnings": warnings,
            "raw_payload": payload,
        }
        return json.dumps(compact, indent=2, default=str)