# Config

Configuration files that control agents, planning constraints, API limits, and resilience settings.

## Files
- `agent_registry.py`: canonical agent IDs and human-readable descriptions.
- `agent_executor.py`: maps agent IDs to executable functions.
- `planner_constraints.py`: strict planner prompt and required JSON schema.
- `api.py`: request limits (image size, allowed types, field length).
- `resilience.py`: retries, delays, and timeouts for nodes and agents.
- `settings.py`: placeholder for environment-specific settings.