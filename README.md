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