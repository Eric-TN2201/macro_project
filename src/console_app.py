# console_app.py – interactive menu-driven CLI for the analysis system.
# Run with: python -m src.console_app
from src.services.workflow_service import WorkflowService


class ConsoleApp:
    """Menu-driven console application for macroinvertebrate image analysis."""

    def __init__(self, workflow_service: WorkflowService) -> None:
        self.workflow_service = workflow_service

    def show_menu(self) -> None:
        """Display the main application menu."""
        print("\n" + "=" * 55)
        print("Macroinvertebrate Image Analysis System")
        print("=" * 55)
        print("1. Show dataset summary")
        print("2. Generate EDA outputs")
        print("3. Train classifier")
        print("4. Predict an image")
        print("5. Run full pipeline")
        print("6. Exit")
        print("=" * 55)

    def run(self) -> None:
        """Run the menu loop until the user chooses to exit."""
        while True:
            self.show_menu()
            choice = input("Select an option: ").strip()

            if choice == "1":
                self.handle_show_summary()       # Display dataset statistics

            elif choice == "2":
                self.handle_generate_eda()       # Save EDA charts and CSVs

            elif choice == "3":
                self.handle_train_classifier()   # Train RandomForest model

            elif choice == "4":
                self.handle_predict_image()      # Classify a single image

            elif choice == "5":
                self.handle_full_pipeline()      # EDA + training in one go

            elif choice == "6":
                print("\nExiting application. Goodbye!")
                break  # Exit the loop to terminate the program

            else:
                print("\nInvalid option. Please choose a number from 1 to 6.")

    def handle_show_summary(self) -> None:
        """Handle dataset summary option."""
        try:
            self.workflow_service.show_summary()
        except Exception as error:
            print(f"\nError while showing summary: {error}")

    def handle_generate_eda(self) -> None:
        """Handle EDA generation option."""
        try:
            self.workflow_service.generate_eda()
        except Exception as error:
            print(f"\nError while generating EDA outputs: {error}")

    def handle_train_classifier(self) -> None:
        """Handle model training option."""
        try:
            self.workflow_service.train_model()
        except Exception as error:
            print(f"\nError while training classifier: {error}")

    def handle_predict_image(self) -> None:
        """Handle image prediction option."""
        image_path = input("\nEnter image path: ").strip()

        # Do not proceed if the user entered an empty string
        if not image_path:
            print("\nImage path cannot be empty.")
            return

        try:
            self.workflow_service.predict_image(image_path)
        except FileNotFoundError as error:
            # Path does not point to an existing file
            print(f"\nFile error: {error}")
        except ValueError as error:
            # Image could not be read or processed
            print(f"\nImage error: {error}")
        except Exception as error:
            print(f"\nError while predicting image: {error}")

    def handle_full_pipeline(self) -> None:
        """Handle full pipeline option."""
        try:
            self.workflow_service.run_full_pipeline()
        except Exception as error:
            print(f"\nError while running full pipeline: {error}")


def main() -> None:
    """Start the console application."""
    # Build the service layer and hand it to the console UI
    workflow_service = WorkflowService()
    app = ConsoleApp(workflow_service)
    app.run()


if __name__ == "__main__":
    main()