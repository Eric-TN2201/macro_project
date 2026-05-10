# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System


from src.services.workflow_service import WorkflowService


def main() -> None:
    """Run the main project workflow."""
    # Create the workflow coordinator which wires all services together
    workflow = WorkflowService()
    # Execute Stage 1 (EDA) and Stage 2 (model training) in sequence
    workflow.run_full_pipeline()


if __name__ == "__main__":
    main()