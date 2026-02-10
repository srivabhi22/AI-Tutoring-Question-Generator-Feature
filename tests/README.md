# Tests

Pytest suite covering API, pipeline behavior, and resilience features.

## Files
- `test_api.py`: FastAPI health and generate endpoints with dependency overrides.
- `test_execution_order.py`: task execution ordering and state updates.
- `test_imports.py`: basic import health checks.
- `test_pipeline_dry_run.py`: pipeline dry run with stubs/fakes.
- `test_plan_validation.py`: planner schema validation and fallback behavior.
- `test_resilience.py`: retry, timeout, and fallback behavior for nodes and agents.

## Run
```
pytest -q
```