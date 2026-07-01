import json
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

        fuji_base_url = base_url or os.getenv("FUJI_BASE_URL")
        if not fuji_base_url:
            raise ValueError("FUJI_BASE_URL is not set")

        self.base_url = fuji_base_url.rstrip("/") + "/evaluate"
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
        except httpx.TimeoutException as exc:
            raise RuntimeError("F-UJI request timed out") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"F-UJI request failed: {exc}") from exc

        summary = payload.get("summary", {})
        results = payload.get("results", [])
        resolved_url = payload.get("resolved_url") or metadata.identifier
        metric_version = payload.get("metric_version")
        software_version = payload.get("software_version")

        notes = self._extract_notes(results)
        warnings: list[str] = []

        if metric_version:
            notes.append(f"metric_version: {metric_version}")
        if software_version:
            notes.append(f"software_version: {software_version}")

        overall_score = self._extract_overall_score(summary, warnings)
        principle_scores = PrincipleScores(
            findable=self._extract_principle_score(summary, "F", warnings),
            accessible=self._extract_principle_score(summary, "A", warnings),
            interoperable=self._extract_principle_score(summary, "I", warnings),
            reusable=self._extract_principle_score(summary, "R", warnings),
        )

        llm_context = self._build_llm_context(
            metadata_identifier=metadata.identifier,
            resolved_url=resolved_url,
            summary=summary,
            notes=notes,
            warnings=warnings,
            payload=payload,
        )

        return ToolResult(
            tool_name="f-uji",
            overall_score=overall_score,
            principle_scores=principle_scores,
            raw_summary=f"F-UJI assessed resource {resolved_url}.",
            notes=notes,
            raw_payload=payload,
            llm_context=llm_context,
            warnings=warnings,
            error=None,
        )

    def _extract_overall_score(self, summary: dict[str, Any], warnings: list[str]) -> float | None:
        score_percent = summary.get("score_percent") or summary.get("scorepercent")

        if isinstance(score_percent, dict):
            fair_value = score_percent.get("FAIR")
            if isinstance(fair_value, (int, float, str)):
                try:
                    return round(float(fair_value) / 100, 2)
                except (TypeError, ValueError):
                    warnings.append("Could not parse summary.scorepercent['FAIR'] as numeric.")
                    return None

        if isinstance(score_percent, (int, float, str)):
            try:
                return round(float(score_percent) / 100, 2)
            except (TypeError, ValueError):
                warnings.append("Could not parse summary.scorepercent as numeric.")

        score = summary.get("score")
        ratio = self._score_ratio(score)
        if ratio is not None:
            return ratio

        warnings.append("Could not extract normalized overall score from F-UJI summary.")
        return None

    def _extract_principle_score(
            self,
            summary: dict[str, Any],
            principle: str,
            warnings: list[str],
    ) -> float | None:
        score_percent = summary.get("score_percent") or summary.get("scorepercent")

        if isinstance(score_percent, dict):
            value = score_percent.get(principle)
            if isinstance(value, (int, float, str)):
                try:
                    return round(float(value) / 100, 2)
                except (TypeError, ValueError):
                    warnings.append(
                        f"Could not parse summary.scorepercent['{principle}'] as numeric."
                    )

        fair_percentage = summary.get("fair_percentage_by_principle", {})
        if isinstance(fair_percentage, dict):
            value = fair_percentage.get(principle)
            if isinstance(value, (int, float, str)):
                try:
                    return round(float(value) / 100, 2)
                except (TypeError, ValueError):
                    warnings.append(
                        f"Could not parse fair_percentage_by_principle['{principle}'] as numeric."
                    )

        score_by_principle = summary.get("score_by_principle", {})
        if isinstance(score_by_principle, dict):
            ratio = self._score_ratio(score_by_principle.get(principle))
            if ratio is not None:
                return ratio

        return None

    def _score_ratio(self, score_obj: Any) -> float | None:
        if not isinstance(score_obj, dict):
            return None

        earned = score_obj.get("earned", 0)
        total = score_obj.get("total", 0)

        try:
            earned = float(earned)
            total = float(total)
        except (TypeError, ValueError):
            return None

        if total == 0:
            return None

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

    def _build_llm_context(
        self,
        metadata_identifier: str,
        resolved_url: str,
        summary: dict[str, Any],
        notes: list[str],
        warnings: list[str],
        payload: dict[str, Any],
    ) -> str:
        compact = {
            "tool": "f-uji",
            "input_identifier": metadata_identifier,
            "resolved_url": resolved_url,
            "summary": summary,
            "notes": notes,
            "warnings": warnings,
            "raw_payload": payload,
        }
        return json.dumps(compact, indent=2, default=str)