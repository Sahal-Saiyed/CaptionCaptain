import os
import json
import time
from dotenv import load_dotenv

# Import our custom structural engines from the src directory
from src.vision import VideoProcessor
from src.llm_engine import CaptionAgent

# Load environment variables (.env)
load_dotenv()


def load_input_tasks(input_path: str) -> list:
    """Loads the execution tasks using strict absolute paths."""
    if os.path.exists(input_path):
        print(f"Loading input tasks from: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"⚠️ Warning: {input_path} not found. Ensure volume is mounted correctly.")
        return []


def main():
    start_time = time.time()
    print("==================================================")
    print("🚀 CAPTAIN CAPTION: RUNTIME INITIALIZATION")
    print("==================================================")

    # UPDATED: Use absolute paths exactly as requested by the evaluation server
    input_file = "/input/tasks.json"
    output_dir = "/output"
    output_file = os.path.join(output_dir, "results.json")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize our pipeline objects
    tasks = load_input_tasks(input_file)
    video_processor = VideoProcessor(target_frames=3, max_width=720)
    caption_agent = CaptionAgent()

    final_output = []

    # Process tasks sequentially
    for idx, task in enumerate(tasks, 1):
        # UPDATED: Use 'task_id' and 'styles' to match the PDF schema
        task_id = task.get("task_id", f"unknown_{idx}")
        video_url = task.get("video_url")
        requested_styles = task.get("styles", ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"])

        print(f"\n[Task {idx}/{len(tasks)}] Processing Task ID: {task_id}")

        if not video_url:
            print(f"❌ Skipping Task {task_id}: Missing video_url.")
            continue

        try:
            # Step 1: Frame Extraction Engine
            base64_frames = video_processor.extract_base64_frames(video_url)

            # Step 2: LLM Analysis Engine
            if base64_frames:
                captions = caption_agent.generate_captions(base64_frames, requested_styles)
            else:
                captions = {style: "Pipeline Error: Could not extract frames." for style in requested_styles}

            # Step 3: UPDATED Payload matching exact expected output schema
            task_result = {
                "task_id": task_id,
                "captions": captions
            }
            final_output.append(task_result)

        except Exception as e:
            print(f"💥 Critical crash caught during processing task {task_id}: {e}")
            final_output.append({
                "task_id": task_id,
                "captions": {style: f"Pipeline Exception: {str(e)}" for style in requested_styles}
            })

    # Save final results to disk
    print(f"\n💾 Compilation complete. Writing final results to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4)

    total_duration = time.time() - start_time
    print("==================================================")
    print(f"✅ EXECUTION SUCCESSFUL")
    print(f"⏱️ Total Runtime Duration: {total_duration:.2f} seconds")
    print("==================================================")


if __name__ == "__main__":
    main()