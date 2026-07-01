import json

from app.adapters.base import BaseFAIRToolAdapter
from app.schemas.compare import PrincipleScores, ToolResult
from app.schemas.metadata import DatasetMetadata


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