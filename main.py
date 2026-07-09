import os
import time

from dotenv import load_dotenv

from src.data_pipeline import CaptionResult, DataManager
from src.llm_engine import CaptionAgent
from src.vision import VideoProcessor

# Load environment variables (.env)
load_dotenv()
print("API:", os.getenv("FIREWORKS_API_KEY"))
print("MODEL:", os.getenv("FIREWORKS_MODEL_NAME"))

def main():
    start_time = time.time()
    print("=" * 50)
    print("🚀 CAPTAIN CAPTION: RUNTIME INITIALIZATION")
    print("=" * 50)

    # Absolute paths as required by the evaluation server
    input_file = "/input/tasks.json"
    output_file = "/output/results.json"

    os.makedirs("/output", exist_ok=True)

    # Use DataManager for validated I/O (Pydantic schema enforcement)
    data_manager = DataManager(input_path=input_file, output_path=output_file)
    tasks = data_manager.load_tasks()

    video_processor = VideoProcessor(target_frames=3, max_width=720)
    caption_agent = CaptionAgent()

    final_output = []

    for idx, task in enumerate(tasks, 1):
        task_id = task.task_id
        video_url = task.video_url
        requested_styles = task.styles

        print(f"\n[Task {idx}/{len(tasks)}] Processing Task ID: {task_id}")

        if not video_url:
            print(f"❌ Skipping Task {task_id}: Missing video_url.")
            continue

        try:
            # Step 1: Frame Extraction Engine
            base64_frames = video_processor.extract_base64_frames(video_url)

            # Step 2: LLM Analysis Engine
            if base64_frames:
                captions = caption_agent.generate_captions(
                    base64_frames, requested_styles
                )
            else:
                captions = {
                    style: "Pipeline Error: Could not extract frames."
                    for style in requested_styles
                }

            # Step 3: Pydantic-validated output matching exact expected schema
            task_result = CaptionResult(task_id=task_id, captions=captions)
            final_output.append(task_result)

        except Exception as e:
            print(f"💥 Critical crash caught during processing task {task_id}: {e}")
            final_output.append(
                CaptionResult(
                    task_id=task_id,
                    captions={
                        style: f"Pipeline Exception: {str(e)}"
                        for style in requested_styles
                    },
                )
            )

    # Save final results via DataManager (validates output schema)
    print(f"\n💾 Compilation complete. Writing final results to: {output_file}")
    data_manager.save_results(final_output)

    total_duration = time.time() - start_time
    print("=" * 50)
    print(f"✅ EXECUTION SUCCESSFUL")
    print(f"⏱️ Total Runtime Duration: {total_duration:.2f} seconds")
    print("=" * 50)


if __name__ == "__main__":
    main()
