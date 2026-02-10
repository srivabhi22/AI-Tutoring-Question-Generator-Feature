# AI Tutoring Question Generator Feature

## Project Structure

```
ai-tutoring-agent/
│
├── README.md
├── pyproject.toml / requirements.txt
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # API keys, model names, env vars
│   ├── agent_registry.py        # AVAILABLE_AGENTS, CAPABILITY_MAP
│   └── planner_constraints.py   # Planner prompt + schema
│
├── core/
│   ├── __init__.py
│   ├── state.py                 # LangGraph State (TypedDict)
│   ├── graph.py                 # LangGraph construction
│   ├── routing.py               # Agent routing + validation
│   └── planner_repair.py        # Plan validation, repair, fallback
│
├── preprocessing/
│   ├── __init__.py
│   ├── text_cleaner.py          # Markdown + LaTeX + chemistry cleanup
│   ├── latex_utils.py           # latex_to_text, arrow normalization
│   └── json_utils.py            # extract_json_from_llm, safe parsing
│
├── agents/
│   ├── __init__.py
│   │
│   ├── multimodal/
│   │   ├── __init__.py
│   │   └── vision_agent.py      # Image → metadata + analysis
│   │
│   ├── planner/
│   │   ├── __init__.py
│   │   └── planner_agent.py     # Produces plan JSON
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── content_analyzer.py
│   │   └── exam_pattern_analyst.py
│   │
│   ├── design/
│   │   ├── __init__.py
│   │   └── question_designer.py
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   └── question_generator.py
│   │
│   ├── solving/
│   │   ├── __init__.py
│   │   └── solver_agent.py
│   │
│   └── evaluation/
│       ├── __init__.py
│       └── evaluator_agent.py
│
├── tools/
│   ├── __init__.py
│   ├── math_solver.py           # (optional) symbolic/numeric tools
│   └── units.py                 # (optional) unit normalization
│
├── interfaces/
│   ├── __init__.py
│   ├── cli.py                   # CLI entry point
│   └── api.py                   # FastAPI / Flask later
│
├── tests/
│   ├── test_preprocessing.py
│   ├── test_planner.py
│   ├── test_agents.py
│   └── test_graph.py
│
└── main.py                      # Single entry point
```

## Directory Overview

### `/config`
Configuration files for the application including API credentials, agent registry, and planner constraints.

### `/core`
Core functionality including LangGraph state management, graph construction, routing logic, and plan validation.

### `/preprocessing`
Text preprocessing utilities for cleaning Markdown, LaTeX, chemistry notation, and JSON parsing.

### `/agents`
Specialized agents organized by functionality:
- **multimodal**: Vision processing for images
- **planner**: Strategic planning and task decomposition
- **analysis**: Content and exam pattern analysis
- **design**: Question design and structure
- **generation**: Question content generation
- **solving**: Problem-solving capabilities
- **evaluation**: Quality assessment and validation

### `/tools`
Optional utility tools for mathematical operations and unit conversions.

### `/interfaces`
User-facing interfaces including CLI and future API endpoints.

### `/tests`
Comprehensive test suite covering all major components.


Command to start the fastapi app:
```
python -m uvicorn interfaces.api:app --reload --host 0.0.0.0 --port 8000
```

Command to access api endpoint /generate:
```
curl.exe -X POST "http://127.0.0.1:8000/generate" -F "class=11" -F "board=CBSE" -F "target_exam=NEET" -F "image=@data3.png"
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

Test in the container:
```
docker run --rm --env-file .env ai-tutoring pytest -q
```
After containerization:
command to access /generate endpoint
```
curl.exe -X POST "http://127.0.0.1:8000/generate" -F "class=11" -F "board=CBSE" -F "target_exam=NEET" -F "image=@data3.png"
```
or more general command (if path has spaces)
```
curl.exe -X POST "http://127.0.0.1:8000/generate" -F "class=11" -F "board=CBSE" -F "target_exam=NEET" -F "image=@\"C:\Users\HP\My Images\data3.png\""
```

or more general command (if path does not have spaces)
```
curl.exe -X POST "http://127.0.0.1:8000/generate" -F "class=11" -F "board=CBSE" -F "target_exam=NEET" -F "image=@C:\Users\HP\Pictures\data3.png"
```

NOTE: If you want to restart a stopped container without recreating it, run it once without --rm, then use docker start <container_name> (you’d need to name it with --name).