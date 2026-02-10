# Core

The pipeline backbone: LangGraph construction, routing, state schema, and resilience helpers.

## Files
- `graph.py`: builds the LangGraph state machine and node ordering.
- `routing.py`: executes planner-defined tasks in order and merges outputs into state.
- `state.py`: Pydantic models for pipeline state, snapshots, and diagnostics.
- `planner_repair.py`: validates planner output, repairs common errors, and defines fallback plans.
- `resilience.py`: shared retry/timeout/fallback wrapper used by nodes and agents.
- `llm_loader.py`: loads the LLM client from environment configuration.
- `logging_config.py`: central logging setup and log file rotation.