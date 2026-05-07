from src.services.workflow_service import WorkflowService


def main() -> None:
    """Run the main project workflow."""
    workflow = WorkflowService()
    workflow.run_full_pipeline()


if __name__ == "__main__":
    main()