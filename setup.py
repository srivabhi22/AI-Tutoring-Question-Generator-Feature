#!/usr/bin/env python3
"""
Create AI Tutoring Agent Project Structure in current directory
Usage: python setup_structure.py
"""

from pathlib import Path

# Define the complete structure
structure = {
    ".": ["README.md", "pyproject.toml", "requirements.txt", "main.py"],
    "config": ["__init__.py", "settings.py", "agent_executor.py", "agent_registry.py", "planner_constraints.py"],
    "core": ["__init__.py", "state.py", "graph.py", "routing.py", "planner_repair.py"],
    "preprocessing": ["__init__.py", "text_cleaner.py", "latex_utils.py", "json_utils.py"],
    "agents": ["__init__.py"],
    "agents/multimodal": ["__init__.py", "vision_agent.py"],
    "agents/planner": ["__init__.py", "planner_agent.py"],
    "agents/analysis": ["__init__.py", "content_analyzer.py", "exam_pattern_analyst.py"],
    "agents/design": ["__init__.py", "question_designer.py"],
    "agents/generation": ["__init__.py", "question_generator.py"],
    "agents/solving": ["__init__.py", "solver_agent.py"],
    "agents/evaluation": ["__init__.py", "evaluator_agent.py"],
    "tools": ["__init__.py", "math_solver.py", "units.py"],
    "interfaces": ["__init__.py", "cli.py", "api.py"],
    "tests": ["test_preprocessing.py", "test_planner.py", "test_agents.py", "test_graph.py"],
}


def create_structure():
    """Create the complete project structure in current directory."""

    print("Creating project structure in current directory...")

    # Create all directories and files
    for directory, files in structure.items():
        # Create directory
        dir_path = Path(directory)
        if directory != ".":
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create files
        for file in files:
            file_path = dir_path / file
            file_path.touch(exist_ok=True)
            print(f"✓ Created: {file_path}")

    print("\n✓ Project structure created successfully!\n")
    print("Next steps:")
    print("1. Initialize git: git init")
    print("2. Create virtual environment: python -m venv venv")
    print("3. Activate venv:")
    print("   - Linux/Mac: source venv/bin/activate")
    print("   - Windows: venv\\Scripts\\activate")
    print("4. Install dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    create_structure()