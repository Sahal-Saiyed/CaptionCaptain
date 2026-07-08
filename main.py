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
    """Loads the execution tasks. Falls back to a robust mock sample if file missing."""
    if os.path.exists(input_path):
        print(f"Loading input tasks from: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"⚠️ Warning: {input_path} not found. Generating default hackathon evaluation sample...")
        # Create input directory if missing
        os.makedirs(os.path.dirname(input_path), exist_ok=True)

        default_tasks = [
            {
                "video_id": "task_001",
                "video_url": "https://storage.googleapis.com/amd-hackathon-clips/1860079-uhd_2560_1440_25fps.mp4",
                "requested_styles": ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
            }
        ]
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(default_tasks, f, indent=4)
        return default_tasks


def main():
    start_time = time.time()
    print("==================================================")
    print("🚀 CAPTAIN CAPTION: RUNTIME INITIALIZATION")
    print("==================================================")

    # Define strict input and output routing paths
    input_file = os.path.join("input", "tasks.json")
    output_dir = "output"
    output_file = os.path.join(output_dir, "results.json")
    os.makedirs(output_dir, exist_ok=True)

    # Initialize our pipeline objects
    tasks = load_input_tasks(input_file)
    video_processor = VideoProcessor(target_frames=3, max_width=720)  # 3 frames balanced for speed/accuracy
    caption_agent = CaptionAgent()

    final_output = []

    # Process tasks sequentially
    for idx, task in enumerate(tasks, 1):
        video_id = task.get("video_id", f"unknown_{idx}")
        video_url = task.get("video_url")
        requested_styles = task.get("requested_styles", ["formal"])

        print(f"\n[Task {idx}/{len(tasks)}] Processing Video ID: {video_id}")

        if not video_url:
            print(f"❌ Skipping Task {video_id}: Missing video_url.")
            continue

        try:
            # Step 1: Frame Extraction Engine
            base64_frames = video_processor.extract_base64_frames(video_url)

            # Step 2: LLM Analysis Engine
            if base64_frames:
                captions = caption_agent.generate_captions(base64_frames, requested_styles)
            else:
                captions = {style: "Pipeline Error: Could not extract frames." for style in requested_styles}

            # Step 3: Package result object matching expected pipeline structures
            task_result = {
                "video_id": video_id,
                "video_url": video_url,
                "captions": captions
            }
            final_output.append(task_result)

        except Exception as e:
            print(f"💥 Critical crash caught during processing task {video_id}: {e}")
            # Ensure the pipeline doesn't stop for other videos if one single URL crashes
            final_output.append({
                "video_id": video_id,
                "video_url": video_url,
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