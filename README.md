# 🎬 CaptionCaptain: Multimodal Video Context Engine

**Submission for AMD Developer Hackathon ACT II - Track 2 (Video Captioning)**

CaptionCaptain is a resilient, headless video processing pipeline that automatically extracts keyframes from video streams and leverages Vision-Language Models (VLMs) to generate context-aware captions in multiple distinct tones. 

Built specifically for automated evaluation, this pipeline operates entirely within a Dockerized environment, ensuring 100% reproducibility and zero human-in-the-loop dependencies.

## 🚀 Quick Start (For Judges)

This project is fully containerized and expects `input` and `output` volumes to be mounted at runtime. 

**1. Clone the repository**
\`\`\`bash
git clone https://github.com/your-username/CaptionCaptain.git
cd CaptionCaptain
\`\`\`

**2. Configure Environment**
Create a `.env` file in the root directory and add your Fireworks AI key:
\`\`\`env
FIREWORKS_API_KEY=your_api_key_here
FIREWORKS_MODEL_NAME=accounts/fireworks/models/qwen3p7-plus
\`\`\`

**3. Build and Run via Docker**
\`\`\`bash
# Build the image (use --platform linux/amd64 for Apple Silicon / Windows ARM)
docker build --platform linux/amd64 -t caption-captain .

# Run the container with volume mounts
docker run --rm --env-file .env -v "${PWD}/input:/input" -v "${PWD}/output:/output" caption-captain
\`\`\`
*The pipeline will read from `/input/tasks.json` and generate `/output/results.json`.*

---

## 🧠 Core Architecture & Strategic Decisions

To ensure the pipeline completes within the strict 10-minute timeout limit while maintaining high accuracy, we designed three isolated "engines":

### 1. Vision Engine (`vision.py`)
* **Intelligent Extraction:** Uses OpenCV (`opencv-python-headless`) to read video streams directly from URLs, mathematically calculating intervals to extract 3 evenly spaced frames.
* **Payload Optimization:** Full 4K frames are instantly downscaled to 720p and JPEG-compressed before Base64 encoding. This prevents API bloat and massive token costs.

### 2. LLM Engine (`llm_engine.py`)
* **Model Selection:** We utilized **Qwen 3.7 Plus** via the Fireworks AI serverless API (powered by AMD infrastructure). Qwen was strategically chosen for its superior ability to parse dry, sarcastic nuances required by the prompt instructions.
* **In-Context Few-Shot Prompting:** The system prompt injects 4 distinct handcrafted examples (Formal, Sarcastic, Humorous Tech, Humorous Non-Tech) to guide the VLM's spatial reasoning.
* **The Regex Shield:** Open-source models occasionally "think out loud." Instead of relying on brittle markdown parsing, we implemented a robust Regular Expression (`re.search(r'\{.*\}', re.DOTALL)`) to magnetically extract the JSON dictionary, completely ignoring any hallucinated text before or after.

### 3. Master Orchestrator (`main.py`)
* **Headless Design:** Streamlit/UI interfaces freeze automated evaluation servers. This orchestrator is purely headless, looping through tasks, handling network crash exceptions gracefully via `try/except` blocks, and ensuring the final JSON payload is written safely to disk.

---

## 📂 Directory Structure

\`\`\`text
CaptionCaptain/
├── src/
│   ├── __init__.py
│   ├── vision.py          # Frame extraction and compression logic
│   ├── llm_engine.py      # VLM payload construction and Regex parsing
│   └── data_pipeline.py   # Pydantic I/O validation for input/output schemas
├── input/
│   └── tasks.json       # Target video URLs (mounted at runtime)
├── output/
│   └── results.json     # Generated captions (mounted at runtime)
├── Dockerfile           # Python 3.11-slim container instructions
├── .dockerignore        # Context optimization
├── requirements.txt     # Python dependencies
├── .env                 # API Credentials
└── main.py              # Execution entry point
\`\`\`