import json
import os
import re
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()
import fireworks.client


class CaptionAgent:
    def __init__(self):
        self.api_key = os.getenv("FIREWORKS_API_KEY")
        if not self.api_key:
            print("CRITICAL WARNING: FIREWORKS_API_KEY is not set in the .env file!")

        self.model = os.getenv("FIREWORKS_MODEL_NAME")
        if not self.model:
            print("CRITICAL WARNING: FIREWORKS_MODEL_NAME is not set in the .env file!")

        fireworks.client.api_key = self.api_key

    def _build_system_prompt(self) -> str:
        return """You are an expert video captioning agent. You are given a sequence of frames from a short video.
Your task is to analyze the frames and generate a caption for the video in four specific styles.

REQUIRED STYLES AND TONE EXAMPLES:
1. "formal": Professional, objective, factual tone.
2. "sarcastic": Dry, ironic, lightly mocking.
3. "humorous_tech": Funny, with technology or programming references.
4. "humorous_non_tech": Funny, everyday humour with no technical jargon.

CRITICAL INSTRUCTION:
You must return ONLY a valid JSON object. The keys must be exactly: "formal", "sarcastic", "humorous_tech", "humorous_non_tech".
DO NOT think out loud. DO NOT explain your reasoning. Output absolutely NO text before or after the JSON object.
"""

    def generate_captions(
        self, base64_frames: List[str], requested_styles: List[str]
    ) -> Dict[str, str]:
        if not base64_frames:
            return {
                style: "Error: No visual data provided." for style in requested_styles
            }

        system_prompt = self._build_system_prompt()

        content = [
            {
                "type": "text",
                "text": "Analyze these frames and output the JSON object with the requested captions.",
            }
        ]
        for b64 in base64_frames:
            content.append({"type": "image_url", "image_url": {"url": b64}})

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ]

        try:
            print(
                f"Sending {len(base64_frames)} frames to Fireworks AI using {self.model}..."
            )
            response = fireworks.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=1200,  # Increased token limit so it doesn't get cut off
            )

            raw_output = response.choices[0].message.content.strip()

            # 🛡️ THE SHIELD: Use Regex to find the JSON block, even if the model is chatty
            json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

            if not json_match:
                raise ValueError("Regex could not find a JSON object in the output.")

            clean_json_string = json_match.group(0)
            generated_json = json.loads(clean_json_string)

            # Verify required keys
            safe_results = {}
            for style in requested_styles:
                safe_results[style] = generated_json.get(
                    style, f"Fallback: Failed to generate {style} tone."
                )

            return safe_results

        except json.JSONDecodeError:
            print(f"ERROR: Found JSON block, but it was invalid formatting.")
            return {
                style: "Fallback: Invalid JSON returned by model."
                for style in requested_styles
            }
        except Exception as e:
            print(f"CRITICAL API ERROR: {e}")
            return {
                style: "Fallback: API failure during generation."
                for style in requested_styles
            }


# --- Local Testing Block ---
if __name__ == "__main__":
    try:
        from vision import VideoProcessor
    except ImportError:
        from src.vision import VideoProcessor

    agent = CaptionAgent()
    print(f"\nInitiating end-to-end dry-run test with {agent.model}...")

    print("\nExtracting 1 real frame for testing...")
    processor = VideoProcessor(target_frames=1)
    test_url = "https://storage.googleapis.com/amd-hackathon-clips/1860079-uhd_2560_1440_25fps.mp4"
    real_frames = processor.extract_base64_frames(test_url)

    if real_frames:
        dummy_styles = ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
        result = agent.generate_captions(real_frames, dummy_styles)
        print("\nAPI Response:")
        print(json.dumps(result, indent=4))
    else:
        print("Failed to extract the test frame.")
