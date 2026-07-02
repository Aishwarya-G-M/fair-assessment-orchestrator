# FAIR Assessment Orchestrator

A lightweight orchestration layer for running automated FAIR assessments against the same digital object, normalizing heterogeneous outputs, and returning a consistent response that applications can actually use.

Automated FAIR assessment tools often expose different APIs, scoring schemes, metric vocabularies, and response formats. Tools such as F-UJI and FAIR-Checker assess overlapping FAIR concepts, but they do not return results in the same structure or level of granularity.[1][2] This project adds value by standardizing those outputs behind a single API contract, making it easier to compare results, build frontend experiences, and tolerate failures from individual upstream tools.[1][3]

## Why this project matters

Most FAIR assessment tools are useful in isolation, but they are hard to integrate directly into an application because they differ in:

- Input expectations
- Output schemas
- Metric naming
- Score scales
- Error behavior
- Timeout patterns

This orchestrator solves that integration problem by acting as a translation and comparison layer between external FAIR assessors and your application.

## What it does

- Accepts a FAIR assessment request for a dataset, DOI, or digital object identifier.
- Invokes one or more FAIR assessment adapters such as F-UJI and FAIR-Checker.[1]
- Normalizes tool-specific outputs into a shared response model.
- Computes overall and principle-level differences across tools.
- Optionally generates a concise LLM-based comparison summary.
- Returns a single stable response contract for frontend and downstream consumers.
- Creates a foundation for graceful degradation when one upstream assessment service fails or times out.

## Core value for applications

This project is not just a proxy. It strengthens an application in four concrete ways:

### 1. Consistent API contract

Instead of forcing the frontend to understand multiple third-party response formats, the orchestrator exposes one predictable response shape. That reduces coupling, simplifies UI logic, and makes the assessment layer easier to evolve.

### 2. Cross-tool comparison

The orchestrator makes it possible to compare multiple FAIR tools side by side. That is especially useful because automated FAIR tools can differ in interpretation, scope, and implementation of FAIR metrics.[1]

### 3. Better failure handling

External tools can be slow, unavailable, or timeout-prone. The orchestrator creates a clean place to implement retries, partial results, timeout controls, and tool-specific error translation.

### 4. Product-ready extensibility

Once the adapter pattern is in place, new assessors can be added without rewriting the application layer. This makes the project a durable platform, not a one-off integration.

## Architecture

The orchestrator is built around a small set of focused components:

| Component | Responsibility |
|---|---|
| Router/API layer | Accepts requests and returns a normalized response |
| Compare service | Coordinates tool execution and comparison logic |
| Adapters | Translate tool-specific APIs into a shared internal model |
| Summary provider | Generates optional natural-language summaries |
| Response schemas | Define the stable contract exposed to consumers |

A typical request flow looks like this:

1. Client sends a DOI or other identifier.
2. The API validates the request.
3. The compare service selects the requested tools.
4. Each adapter calls its external FAIR assessment service.
5. Raw results are normalized into a common `ToolResult` shape.
6. The orchestrator computes score differences and a comparison summary.
7. The API returns a single application-friendly response.

## Supported assessment tools

The orchestrator is designed to work with multiple automated FAIR assessors. F-UJI and FAIR-Checker are two strong examples because both assess FAIR principles but expose different metric styles and outputs.[1]

Current or intended tool support includes:

- F-UJI[1]
- FAIR-Checker[1]
- Additional FAIR evaluators via new adapters

## Example normalized response

A representative compare response can look like this:

```json
{
  "tool_a_result": {
    "tool_name": "f-uji",
    "overall_score": 1.0,
    "principle_scores": {
      "findable": 1.0,
      "accessible": 1.0,
      "interoperable": 1.0,
      "reusable": 1.0
    }
  },
  "tool_b_result": {
    "tool_name": "fair-checker",
    "overall_score": 0.92,
    "principle_scores": {
      "findable": 0.88,
      "accessible": 1.0,
      "interoperable": 0.83,
      "reusable": 1.0
    }
  },
  "score_difference": 0.08,
  "principle_score_difference": {
    "findable": 0.12,
    "accessible": 0.0,
    "interoperable": 0.17,
    "reusable": 0.0
  },
  "comparison_summary": "f-uji scored higher overall than fair-checker.",
  "llm_summary": null,
  "llm_summary_generated": false
}
```

This is the main benefit of the orchestrator: upstream tools may be completely different, but the application receives one coherent response.

## Use cases

This project is useful for:

- Research data portals that want a single FAIR assessment endpoint
- Repository dashboards that compare multiple FAIR tools
- Frontends that need visual FAIR scorecards without parsing raw third-party payloads
- QA workflows for validating FAIR metadata across repositories
- FAIR benchmarking experiments across multiple datasets or DOI providers
- Applications that want optional natural-language summaries of technical FAIR outputs

## Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose, if running in containers
- Network access to the upstream FAIR assessment services you integrate with

### Local setup

```bash
git clone https://github.com/Aishwarya-G-M/fair-assessment-orchestrator.git
cd fair-assessment-orchestrator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If the project uses Poetry instead of `requirements.txt`, use:

```bash
poetry install
poetry shell
```

## Running the orchestrator

Depending on your setup, start the API in one of these ways.

### Run with Uvicorn

```bash
uvicorn app.main:app --reload
```

### Run with Docker Compose

```bash
docker compose up --build
```

Once running, the API should be available locally, typically at:

- `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## How to use the orchestrator

The most important workflow is the compare endpoint.

### Example request

```bash
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_a": "f-uji",
    "tool_b": "fair-checker",
    "metadata": "https://doi.org/10.1594/PANGAEA.902845",
    "include_llm_summary": false
  }'
```

### Example request body

```json
{
  "tool_a": "f-uji",
  "tool_b": "fair-checker",
  "metadata": "https://doi.org/10.1594/PANGAEA.902845",
  "include_llm_summary": true
}
```

### Example response fields

| Field | Description |
|---|---|
| `tool_a_result` | Normalized result from the first selected tool |
| `tool_b_result` | Normalized result from the second selected tool |
| `overall_score` | Tool-level normalized score |
| `principle_scores` | Normalized Findable, Accessible, Interoperable, Reusable scores |
| `score_difference` | Difference between overall scores |
| `principle_score_difference` | Per-principle score difference |
| `comparison_summary` | Simple deterministic summary of the comparison |
| `llm_summary` | Optional natural-language explanation |
| `llm_summary_generated` | Whether an LLM summary was produced |

## How to read the results

Because FAIR tools can use different underlying metrics and logic, the normalized scores should be treated as an application-level comparison layer rather than a claim that all tools measure FAIRness identically.[1] This project is most valuable when it helps users compare assessments consistently, not when it hides the fact that upstream tools have methodological differences.[1][2]

## Example workflows

### 1. Compare two FAIR tools for a single DOI

Use the compare endpoint with the same DOI and two different tools to observe how their normalized outputs differ.

### 2. Build a FAIR scorecard UI

Use the normalized response to render:

- Overall score cards
- FAIR principle bars
- Tool-vs-tool deltas
- Human-readable summary text

### 3. Batch-assess multiple identifiers

Wrap the compare endpoint in a simple script to evaluate a list of DOIs and persist the normalized results for analysis.

## Adding a new adapter

The adapter pattern is what makes the orchestrator scalable.

To add a new FAIR assessment tool:

1. Create a new adapter class.
2. Implement a common method such as `assess(metadata) -> ToolResult`.
3. Translate raw upstream output into the shared internal schema.
4. Register the adapter in dependency injection or service configuration.
5. Add tests for normalization and error handling.

### Adapter pseudo-example

```python
class NewToolAdapter:
    def assess(self, metadata: str) -> ToolResult:
        raw = call_external_service(metadata)
        return ToolResult(
            tool_name="new-tool",
            overall_score=normalize_overall(raw),
            principle_scores=normalize_principles(raw),
            raw_payload=raw,
        )
```

## Error handling recommendations

To make the application stronger, the orchestrator should explicitly handle:

- Upstream timeouts
- Invalid identifiers
- Network failures
- Partial success when one tool works and another fails
- Non-comparable or missing principle scores
- LLM summary failures that should not block the main response

A production-grade strategy is to return partial results with explicit error fields instead of failing the entire comparison when one external tool is unavailable.

## Testing

Run tests with:

```bash
pytest
```

Recommended test coverage includes:

- Adapter normalization tests
- Compare service behavior
- Error propagation tests
- Partial-failure tests
- API smoke tests
- Schema validation tests

## Project strengths

This orchestrator is strongest when positioned as an integration and product-enablement layer rather than just an assessment client. FAIR tools exist to measure FAIRness, but this project makes them usable inside modern applications by providing comparison, normalization, and a stable developer-friendly API.[1][3]

## Roadmap

Suggested roadmap items:

- Graceful partial-result responses when one tool times out
- Retry and timeout configuration per adapter
- Support for more FAIR evaluators
- Batch assessment endpoint
- Persistent storage for historical assessments
- Caching repeated DOI evaluations
- Rich LLM summaries with explanation of score differences
- Frontend dashboard for FAIR comparison visualization
- Export to JSON and CSV reports

## Limitations

- Upstream FAIR tools can timeout or change behavior independently of this project.
- Normalized comparison is useful, but it cannot erase differences in tool methodology.[1]
- Some repositories or landing pages may expose metadata in ways that one tool handles better than another.
- The quality of comparison depends on how carefully the adapter normalization rules are designed.

## Contributing

Contributions are welcome in the following areas:

- New tool adapters
- Better normalization strategies
- Partial-failure handling
- Better documentation
- More dataset fixtures for testing
- Frontend integration examples

Typical workflow:

```bash
git checkout -b feature/my-improvement
git commit -m "Add improvement"
git push origin feature/my-improvement
```

Then open a pull request with:

- A short description of the change
- Why it improves the orchestrator
- Tests or examples showing expected behavior

## Citation and context

Automated FAIR assessment is an active area with multiple tools that operationalize FAIR principles differently, including F-UJI and FAIR-Checker. That diversity is exactly why an orchestration layer is useful: it helps applications consume multiple FAIR assessments through one dependable interface.


## Maintainer

Repository: [Aishwarya-G-M/fair-assessment-orchestrator](https://github.com/Aishwarya-G-M/fair-assessment-orchestrator)