# AI Tutoring Question Generator

## Overview
This project generates exam-aligned questions from a textbook image and a student profile (class, board, target exam). It uses a LangGraph-based multi-agent pipeline to analyze the content, plan tasks, generate questions, solve them, and evaluate output quality.

## Key Features
- Multimodal intake: image -> metadata + analysis.
- Planner-driven execution: tasks are planned then executed in order.
- Resilience: retries, timeouts, and fallbacks per node/agent.
- FastAPI interface for programmatic access.
- Structured outputs: questions, solutions, evaluation, diagnostics.
- Docker-ready for repeatable deployment.

## Architecture (Pipeline Flow)
1) Multimodal grounding: image -> metadata and analysis
2) Planning: create a task plan that selects agents
3) Execution: run agents in order to produce questions, solutions, evaluation
4) Diagnostics: capture retries, fallbacks, timings, and output counts

## Project Layout
- `agents/` multi-agent implementations (see `agents/README.md`)
- `config/` configuration and registry maps (see `config/README.md`)
- `core/` LangGraph pipeline, routing, and resilience (see `core/README.md`)
- `interfaces/` FastAPI and CLI entry points (see `interfaces/README.md`)
- `preprocessing/` text and JSON cleanup utilities (see `preprocessing/README.md`)
- `tests/` pytest suite (see `tests/README.md`)
- `tools/` optional math/unit utilities (see `tools/README.md`)
- `main.py` local run entry point

## Requirements
- Python 3.12 (3.12 used in Dockerfile)
- A Google Gemini API key in `GEMINI_API_KEY`

Install dependencies:
```
python -m pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

## Run Locally
Start the API server:
```
python -m uvicorn interfaces.api:app --reload --host 0.0.0.0 --port 8000
```

Run the pipeline from the CLI entry point:
```
python main.py
```

## API Usage
Health check:
```
curl.exe http://127.0.0.1:8000/health
```

If you change the host port (example: `-p 9000:8000`), update the URL to use `9000`:
```
curl.exe http://127.0.0.1:9000/health
```

Generate questions:
```
curl.exe -X POST "http://127.0.0.1:8000/generate" \
  -F "class=11" \
  -F "board=CBSE" \
  -F "target_exam=NEET" \
  -F "image=@data3.png"
```


If the image is elsewhere, use an absolute path:
```
curl.exe -X POST "http://127.0.0.1:8000/generate" \
  -F "class=11" \
  -F "board=CBSE" \
  -F "target_exam=NEET" \
  -F "image=@C:\Users\HP\Pictures\data3.png"
```

## Containerization
Build the image:
```
docker build -t ai-tutoring .
```

Run the API (loads `GEMINI_API_KEY` from `.env`):
```
docker run --rm -p 8000:8000 --env-file .env ai-tutoring
```

Or with Docker Compose:
```
docker compose up --build
```

## Testing
Run tests locally:
```
pytest -q
```

Run tests in the container:
```
docker run --rm --env-file .env ai-tutoring pytest -q
```

## Logging and Diagnostics
- `logs/pipeline.log` captures runtime logs.
- `logs/state.jsonl` stores state snapshots (image content is redacted).
- API responses include `diagnostics` with retries, fallbacks, timings, and output counts.

## Configuration
- `config/api.py` input limits and file validation.
- `config/resilience.py` retry and timeout tuning.
- `config/agent_registry.py` allowed agent IDs and descriptions.
- `config/agent_executor.py` maps agent IDs to functions.
- `.env` holds `GEMINI_API_KEY`.
