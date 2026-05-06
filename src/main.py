from src.services.workflow_service import WorkflowService


def main() -> None:
    """Run Stage 1 workflow."""
    workflow = WorkflowService()
    workflow.run_stage_1()


if __name__ == "__main__":
    main()