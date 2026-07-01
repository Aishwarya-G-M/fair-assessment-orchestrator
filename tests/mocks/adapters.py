# tests/mocks/adapters.py
import json

from app.adapters.base import BaseFAIRToolAdapter
from app.schemas.compare import PrincipleScores, ToolResult
from app.schemas.metadata import DatasetMetadata


class MockFUJIAdapter(BaseFAIRToolAdapter):
    def assess(self, metadata: DatasetMetadata) -> ToolResult:
        raw_payload = {
            "tool": "f-uji",
            "mock": True,
            "input_identifier": metadata.identifier,
            "resolved_url": metadata.identifier,
            "summary": {
                "scorepercent": {
                    "FAIR": 0.91 * 100,
                    "F": 0.95 * 100,
                    "A": 0.90 * 100,
                    "I": 0.85 * 100,
                    "R": 0.94 * 100,
                }
            },
            "results": [
                {
                    "metric_identifier": "FsF-F1-01MD",
                    "metric_name": "Metadata and data are assigned a globally unique identifier.",
                    "test_status": "pass",
                },
                {
                    "metric_identifier": "FsF-R1.1-01M",
                    "metric_name": "Metadata includes license information under which data can be reused.",
                    "test_status": "pass",
                },
            ],
        }

        notes = [
            "FsF-F1-01MD: Metadata and data are assigned a globally unique identifier.: pass",
            "FsF-R1.1-01M: Metadata includes license information under which data can be reused.: pass",
            "metric_version: mock",
            "software_version: mock",
        ]

        return ToolResult(
            tool_name="f-uji",
            overall_score=0.91,
            principle_scores=PrincipleScores(
                findable=0.95,
                accessible=0.90,
                interoperable=0.85,
                reusable=0.94,
            ),
            raw_summary=f"Mock F-UJI assessed resource {metadata.identifier}.",
            notes=notes,
            raw_payload=raw_payload,
            llm_context=json.dumps(raw_payload, indent=2),
            warnings=[],
            error=None,
        )


class MockFairCheckerAdapter(BaseFAIRToolAdapter):
    def assess(self, metadata: DatasetMetadata) -> ToolResult:
        raw_payload = {
            "tool": "fair-checker",
            "mock": True,
            "input_identifier": metadata.identifier,
            "overall_score": 0.72,
            "principles": {
                "findable": 0.80,
                "accessible": 0.70,
                "interoperable": 0.65,
                "reusable": 0.73,
            },
            "checks": [
                {"name": "Persistent identifier", "status": "pass"},
                {"name": "Metadata availability", "status": "pass"},
                {"name": "Accessible protocol", "status": "pass"},
                {"name": "Interoperable vocabularies", "status": "warning"},
                {"name": "License information", "status": "pass"},
            ],
        }

        notes = [
            "Persistent identifier: pass",
            "Metadata availability: pass",
            "Accessible protocol: pass",
            "Interoperable vocabularies: warning",
            "License information: pass",
        ]

        return ToolResult(
            tool_name="fair-checker",
            overall_score=0.72,
            principle_scores=PrincipleScores(
                findable=0.80,
                accessible=0.70,
                interoperable=0.65,
                reusable=0.73,
            ),
            raw_summary="Mock assessment from FAIR-Checker.",
            notes=notes,
            raw_payload=raw_payload,
            llm_context=json.dumps(raw_payload, indent=2),
            warnings=[],
            error=None,
        )