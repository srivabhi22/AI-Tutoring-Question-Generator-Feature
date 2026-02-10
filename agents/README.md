# Agents

This directory contains the specialized agents that perform each step in the tutoring pipeline. Each agent is responsible for a focused task and returns structured output for the shared state.

## Subdirectories
- `multimodal/vision_agent.py`: extracts metadata and image analysis from the input image
- `planner/planner_agent.py`: produces a task plan (JSON) that selects which agents run
- `analysis/content_analyzer.py`: extracts core concepts and facts
- `analysis/exam_pattern_analyst.py`: maps content to exam styles and priorities
- `design/question_designer.py`: designs question intent, difficulty, and structure
- `generation/question_generator.py`: generates the final question bank
- `solving/solver_agent.py`: solves questions step-by-step
- `evaluation/evaluator_agent.py`: evaluates solutions and provides feedback

## Extending
When adding a new agent:
1) Add the agent implementation here.
2) Register the ID in `config/agent_registry.py`.
3) Map the ID to its function in `config/agent_executor.py`.
4) Update planner constraints in `config/planner_constraints.py` if needed.