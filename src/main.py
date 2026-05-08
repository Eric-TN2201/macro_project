# main.py – entry point for running the full pipeline from the command line.
# Usage: python -m src.main
from src.services.workflow_service import WorkflowService


def main() -> None:
    """Run the main project workflow."""
    # Create the workflow coordinator which wires all services together
    workflow = WorkflowService()
    # Execute Stage 1 (EDA) and Stage 2 (model training) in sequence
    workflow.run_full_pipeline()


if __name__ == "__main__":
    main()