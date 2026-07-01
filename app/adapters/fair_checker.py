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
        base_url: str = "https://fair-checker.france-bioinformatique.fr/api/check/metrics_all",
    ) -> None:
        self.http_client = http_client or FAIRToolHTTPClient()
        self.base_url = base_url.rstrip("/")

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

        warnings: list[str] = []

        if not isinstance(payload, list):
            warnings.append("FAIR-Checker returned unexpected non-list payload.")
            return ToolResult(
                tool_name="fair-checker",
                raw_payload=payload,
                llm_context=json.dumps(payload, indent=2, default=str),
                warnings=warnings,
                error="Unexpected payload format.",
            )

        measurements = self._parse_measurements(payload)
        notes = [f"{k}: {v}" for k, v in measurements.items()]

        overall = self._overall_score(measurements)
        principle_scores = PrincipleScores(
            findable=self._principle_score(measurements, "F"),
            accessible=self._principle_score(measurements, "A"),
            interoperable=self._principle_score(measurements, "I"),
            reusable=self._principle_score(measurements, "R"),
        )

        llm_context = json.dumps({
            "tool": "fair-checker",
            "input_identifier": metadata.identifier,
            "measurements": measurements,
            "notes": notes,
            "warnings": warnings,
        }, indent=2)

        return ToolResult(
            tool_name="fair-checker",
            overall_score=overall,
            principle_scores=principle_scores,
            raw_summary="Assessment returned by FAIR-Checker.",
            notes=notes,
            raw_payload=payload,
            llm_context=llm_context,
            warnings=warnings,
            error=None,
        )

    def _parse_measurements(self, payload: list) -> dict[str, int]:
        """Returns a dict of metric_id -> integer score value."""
        measurements = {}
        for item in payload:
            if "http://www.w3.org/ns/dqv#QualityMeasurement" not in item.get("@type", []):
                continue
            metric_ref = item.get("http://www.w3.org/ns/dqv#isMeasurementOf", [{}])[0].get("@id", "")
            metric_id = metric_ref.split("/")[-1]  # e.g. "F1A", "I2", "R1.1"
            value_list = item.get("http://www.w3.org/ns/dqv#value", [{}])
            value = value_list[0].get("@value", 0) if value_list else 0
            measurements[metric_id] = int(value)
        return measurements

    def _principle_score(self, measurements: dict[str, int], prefix: str) -> float | None:
        matching = {k: v for k, v in measurements.items() if k.startswith(prefix)}
        if not matching:
            return None
        return round(sum(matching.values()) / (len(matching) * 2), 2)

    def _overall_score(self, measurements: dict[str, int]) -> float | None:
        if not measurements:
            return None
        return round(sum(measurements.values()) / (len(measurements) * 2), 2)

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