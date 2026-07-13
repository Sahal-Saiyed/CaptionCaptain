# 🎬 CaptionCaptain

**CaptionCaptain** is an AI-powered video caption generation application that transforms videos into engaging captions in multiple writing styles. Simply upload a video or provide a video URL, and CaptionCaptain analyzes the video to generate captions tailored to different audiences and creative preferences.

---

## ✨ Features

* 🎥 Upload an MP4 video or provide a video URL
* ✍️ Generate captions in multiple writing styles
* 🎭 Built-in styles include:

  * Formal
  * Sarcastic
  * Humorous (Tech)
  * Humorous (Non-Tech)
* 🌟 Supports custom caption styles beyond the predefined ones
* 💬 Interactive chat-based interface built with Streamlit
* 📹 Floating video preview during the conversation
* ⚡ Fast AI-powered caption generation

---

## 🛠️ Technologies Used

* Python
* Streamlit
* Fireworks AI
* OpenCV
* Pillow (PIL)
* Pydantic
* python-dotenv

---

## 📂 Project Structure

```text
CaptionCaptain/
│
├── app.py                  # Streamlit application
├── main.py                 # Batch processing entry point
├── requirements.txt
├── Dockerfile
├── .env
│
├── src/
    ├── vision.py           # Video frame extraction
    ├── llm_engine.py       # AI caption generation
    └── data_pipeline.py    # Input/output handling
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd CaptionCaptain
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it.

Windows

```bash
.venv\Scripts\activate
```

macOS/Linux

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

```env
FIREWORKS_API_KEY=your_api_key
FIREWORKS_MODEL_NAME=your_model_name
```

### 5. Launch the Streamlit application

```bash
streamlit run app.py
```

---

## 📦 Batch Processing

To process tasks using the evaluation pipeline:

```bash
python main.py
```

The program expects:

* `/input/tasks.json`
* `/output/results.json`

---

## 💡 Use Cases

* Social media captions
* Marketing campaigns
* Content creation
* Creative storytelling
* Brand communication
* Educational content

---

## 📸 How It Works

1. Upload a video or provide a video URL.
2. CaptionCaptain analyzes key moments from the video.
3. AI generates captions in the requested writing styles.
4. View and copy your favorite caption directly from the interface.

---

## 🌟 Custom Styles

While the application includes four predefined styles required for the project, CaptionCaptain also supports additional user-requested writing styles, allowing captions to be tailored for different audiences, platforms, and creative needs.

---

## 📄 License

This project is intended for educational and hackathon purposes.

---

## 🙏 Acknowledgements

Thanks to the hackathon organizers for providing the opportunity to build CaptionCaptain and explore AI-powered video caption generation.
