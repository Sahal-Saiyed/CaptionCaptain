import json
import os
from typing import List, Dict
from pydantic import BaseModel, ValidationError


# --- Pydantic Data Models (The Safety Net) ---
class VideoTask(BaseModel):
    task_id: str
    video_url: str
    styles: List[str]


class CaptionResult(BaseModel):
    task_id: str
    captions: Dict[str, str]


# --- Core Pipeline Logic ---
class DataManager:
    def __init__(self, input_path: str = "/input/tasks.json", output_path: str = "/output/results.json"):
        # Defaulting to the container paths, allowing overrides for local testing
        self.input_path = input_path
        self.output_path = output_path

    def load_tasks(self) -> List[VideoTask]:
        """Reads the input JSON and rigorously validates it."""
        print(f"Loading tasks from {self.input_path}...")
        try:
            with open(self.input_path, 'r') as file:
                raw_data = json.load(file)

            # Pydantic converts raw dictionaries into typed Python objects
            tasks = [VideoTask(**item) for item in raw_data]
            print(f"Successfully loaded {len(tasks)} tasks.")
            return tasks

        except FileNotFoundError:
            print(f"CRITICAL ERROR: Input file not found at {self.input_path}")
            return []
        except ValidationError as e:
            print(f"CRITICAL ERROR: Malformed JSON structure.\n{e}")
            return []

    def save_results(self, results: List[CaptionResult]) -> None:
        """Dumps the final results out to the required output path."""
        print(f"Saving {len(results)} results to {self.output_path}...")

        output_data = [result.model_dump() for result in results]

        # Ensure the output directory exists (crucial for Docker)
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, 'w') as file:
            json.dump(output_data, file, indent=4)

        print("Results saved successfully.")


# --- Local Testing Block ---
if __name__ == "__main__":
    # Create fake local directories to simulate the container
    os.makedirs("./input", exist_ok=True)
    os.makedirs("./output", exist_ok=True)

    # Create a mock input file based on the rulebook
    mock_input = [
        {
            "task_id": "1",
            "video_url": "https://storage.example.com/clips/clip1.mp4",
            "styles": ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
        }
    ]
    with open("./input/tasks.json", 'w') as f:
        json.dump(mock_input, f)

    # Run the test
    manager = DataManager(input_path="./input/tasks.json", output_path="./output/results.json")
    tasks = manager.load_tasks()

    if tasks:
        # Simulate a result
        mock_results = [
            CaptionResult(
                task_id=tasks[0].task_id,
                captions={"formal": "Test", "sarcastic": "Test", "humorous_tech": "Test", "humorous_non_tech": "Test"}
            )
        ]
        manager.save_results(mock_results)
        print("Pipeline test complete. Check the ./output/results.json file.")