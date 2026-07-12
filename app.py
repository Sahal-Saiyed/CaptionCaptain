import streamlit as st
import os
import re
import tempfile
import hashlib
from dotenv import load_dotenv
from src.vision import VideoProcessor
from src.llm_engine import CaptionAgent
from PIL import Image
import base64

# Load environment variables
load_dotenv()

# Page configuration
icon_img = Image.open("CaptionCaptain_Cap_Icon.png")
st.set_page_config(page_title="CaptionCaptain", page_icon=icon_img, layout="centered")

# Global CSS for Tab styling and Avatar Fixes
st.markdown("""
    <style>
    /* Make Streamlit Tab labels bold and sharp */
    button[data-baseweb="tab"] p {
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* Stop Streamlit from cropping the bot avatar into a circle */
    [data-testid="stChatMessageAvatar"] {
        border-radius: 4px !important;
        background-color: transparent !important;
    }
    [data-testid="stChatMessageAvatar"] img {
        border-radius: 4px !important;
        object-fit: contain !important;
    }
    </style>
""", unsafe_allow_html=True)


def get_base64_file(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# Initialize conversational session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Track active video for the floating preview
if "active_video" not in st.session_state:
    st.session_state.active_video = None
if "active_video_is_url" not in st.session_state:
    st.session_state.active_video_is_url = False

# ==========================================
# ⚓ FIXED FLOATING UI (Top Left: Logo + Video)
# ==========================================
if len(st.session_state.messages) > 0:

    # 1. Floating Logo
    logo_path = "CaptionCaptain_Logo.png"
    if os.path.exists(logo_path):
        base64_logo = get_base64_file(logo_path)
        st.markdown(
            f"""
            <style>
            @keyframes slideInFade {{
                0% {{ opacity: 0; transform: translateY(-15px); }}
                100% {{ opacity: 1; transform: translateY(0); }}
            }}
            .fixed-logo {{
                position: fixed;
                top: 60px;      
                left: 20px;     
                width: 240px;   
                z-index: 999999; 
                animation: slideInFade 0.6s ease-out forwards; 
            }}
            </style>
            <img src="data:image/png;base64,{base64_logo}" class="fixed-logo">
            """,
            unsafe_allow_html=True
        )

    # 2. Floating Video Preview (Width pinned to 240px)
    if st.session_state.active_video:
        # 🟢 Create a stable, unique ID for the current video to force the browser to reload it
        vid_id = hashlib.md5(st.session_state.active_video.encode()).hexdigest()
        vid_src = ""

        if st.session_state.active_video_is_url:
            vid_src = st.session_state.active_video
        elif os.path.exists(st.session_state.active_video):
            base64_vid = get_base64_file(st.session_state.active_video)
            vid_src = f"data:video/mp4;base64,{base64_vid}"

        if vid_src:
            # 🟢 Apply the unique ID and inject the src directly into the <video> tag
            st.markdown(
                f"""
                <style>
                .fixed-video {{
                    position: fixed;
                    top: 180px;     
                    left: 20px;     
                    width: 240px;   
                    border-radius: 8px;
                    border: 1px solid #333;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                    z-index: 999998; 
                    animation: slideInFade 0.6s ease-out forwards;
                }}
                </style>
                <video id="vid_{vid_id}" class="fixed-video" src="{vid_src}" controls autoplay muted loop>
                    Your browser does not support the video tag.
                </video>
                """,
                unsafe_allow_html=True
            )

# ==========================================
# 🌌 STATE 1: Empty Chat (Landing Screen)
# ==========================================
if len(st.session_state.messages) == 0:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    # Main Center Logo
    with col2:
        if os.path.exists("CaptionCaptain_Logo.png"):
            st.image("CaptionCaptain_Logo.png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>🎬 CaptionCaptain</h1>", unsafe_allow_html=True)

    st.markdown("""
        <h3 style='text-align: center; font-weight: 300; color: #a8a8b3;'>
        Transforming video pixels into multi-tonal prose.
        </h3>
        <p style='text-align: center; color: #6b6b77;'>
        Paste an MP4 video URL or click the + icon in the chat bar below to attach a file.
        </p>
    """, unsafe_allow_html=True)

# ==========================================
# 💬 STATE 2: Active Chat History
# ==========================================
for message in st.session_state.messages:
    avatar_icon = icon_img if message["role"] == "assistant" else "👤"

    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

        if "captions" in message:
            styles = list(message["captions"].keys())
            tab_titles = [f"{s.replace('_', ' ').title()}" for s in styles]
            tabs = st.tabs(tab_titles)

            for tab, (style, text) in zip(tabs, message["captions"].items()):
                with tab:
                    # Single-line HTML string prevents Python f-string whitespace injection
                    st.markdown(
                        f'<div style="background-color: #F8F9FA; padding: 22px; border-radius: 8px; border-left: 4px solid #4F46E5; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-top: 0px !important; color: #1F2937; font-size: 15px; line-height: 1.6; font-weight: 400; white-space: pre-wrap;">{text.strip()}</div>',
                        unsafe_allow_html=True)

# ==========================================
# 🚀 Pinned Native Chat Input
# ==========================================
user_input = st.chat_input(
    "Paste a video URL or attach an MP4 here to generate captions...",
    accept_file=True,
    file_type=["mp4", "mov", "avi"]
)

# ==========================================
# 🧠 Input Trigger Logic
# ==========================================
if user_input:
    if isinstance(user_input, str):
        text_content = user_input
        uploaded_files = []
    else:
        text_content = user_input.text
        uploaded_files = user_input.get("files", [])

    if uploaded_files:
        uploaded_file = uploaded_files[0]
        file_bytes = uploaded_file.read()

        # Save directly to the project folder to bypass Windows Temp folder permission problems
        fd, temp_path = tempfile.mkstemp(suffix=".mp4")
        os.close(fd)
        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        display_text = text_content if text_content else f"Please process my attached file: {uploaded_file.name}"
        st.session_state.messages.append({
            "role": "user",
            "content": display_text,
            "video_path": temp_path,
            "file_name": uploaded_file.name
        })

        st.session_state.active_video = temp_path
        st.session_state.active_video_is_url = False
    else:
        st.session_state.messages.append({"role": "user", "content": text_content})

        url_match = re.search(r'(https?://[^\s]+)', text_content)
        if url_match:
            st.session_state.active_video = url_match.group(0)
            st.session_state.active_video_is_url = True

    st.rerun()

# ==========================================
# ⚙️ Processing Pipeline
# ==========================================
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]

    with st.chat_message("assistant", avatar=icon_img):
        video_source = None

        # Standardize paths to use forward slashes for cross-OS compatibility
        if "video_path" in last_msg and os.path.exists(last_msg["video_path"]):
            video_source = last_msg["video_path"].replace("\\", "/")
            st.markdown(f"🔍 **Detected attached video:** `{last_msg['file_name']}`")
        else:
            url_match = re.search(r'(https?://[^\s]+)', last_msg["content"])
            if url_match:
                video_source = url_match.group(0)
                st.markdown(f"🔍 **Detected video source:** `{video_source}`")
            else:
                error_text = "I am ready to process your video! Please include a valid video URL or attach a file using the + icon."
                st.markdown(error_text)
                st.session_state.messages.append({"role": "assistant", "content": error_text})

        if video_source:
            try:
                loading_placeholder = st.empty()
                base_path = "CaptionCaptain_Logo_Base.png"
                spinner_path = "CaptionCaptain_Logo_Spinner.png"

                if os.path.exists(base_path) and os.path.exists(spinner_path):
                    base64_base = get_base64_file(base_path)
                    base64_spinner = get_base64_file(spinner_path)
                    with loading_placeholder.container():
                        st.markdown(
                            f"""
                            <style>
                            @keyframes scrollUpLoop {{
                                0% {{ transform: translateY(100%); opacity: 0; }}
                                20% {{ transform: translateY(0); opacity: 1; }}
                                80% {{ transform: translateY(0); opacity: 1; }}
                                100% {{ transform: translateY(-100%); opacity: 0; }}
                            }}
                            .loader-container {{
                                position: relative;
                                width: 120px; 
                                height: 120px;
                                margin: 0 auto; 
                                overflow: hidden; 
                            }}
                            .loader-base {{
                                position: absolute;
                                top: 0; left: 0;
                                width: 100%; height: 100%;
                                object-fit: contain;
                                z-index: 1; 
                            }}
                            .loader-spinner {{
                                position: absolute;
                                top: 0; left: 0;
                                width: 100%; height: 100%;
                                object-fit: contain;
                                z-index: 2; 
                                animation: scrollUpLoop 2s cubic-bezier(0.4, 0.0, 0.2, 1) infinite; 
                            }}
                            .loader-text {{
                                text-align: center;
                                font-family: monospace;
                                color: #a8a8b3;
                                margin-top: 20px;
                                font-size: 14px;
                            }}
                            </style>
                            <div class="loader-container">
                                <img src="data:image/png;base64,{base64_base}" class="loader-base">
                                <img src="data:image/png;base64,{base64_spinner}" class="loader-spinner">
                            </div>
                            <div class="loader-text">Processing request...</div>
                            <br>
                            """,
                            unsafe_allow_html=True
                        )

                processor = VideoProcessor(target_frames=8, max_width=1024)
                base64_frames = processor.extract_base64_frames(video_source)

                if not base64_frames:
                    loading_placeholder.empty()
                    st.error("Failed to parse video. Please verify the URL or ensure the file is not corrupted.")
                else:
                    agent = CaptionAgent()
                    styles = ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
                    generated_captions = agent.generate_captions(base64_frames, styles)

                    loading_placeholder.empty()
                    st.toast("Captions generated successfully!")

                    # Render the Interactive Tabs interface dynamically on finish
                    styles_keys = list(generated_captions.keys())
                    tab_titles = [f"{s.replace('_', ' ').title()}" for s in styles_keys]
                    tabs = st.tabs(tab_titles)

                    for tab, (style, text) in zip(tabs, generated_captions.items()):
                        with tab:
                            # Single-line HTML string prevents Python f-string whitespace injection
                            st.markdown(
                                f'<div style="background-color: #F8F9FA; padding: 22px; border-radius: 8px; border-left: 4px solid #4F46E5; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-top: 0px !important; color: #1F2937; font-size: 15px; line-height: 1.6; font-weight: 400; white-space: pre-wrap;">{text.strip()}</div>',
                                unsafe_allow_html=True)

                    # Save to state history perfectly, exactly once
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I've analyzed the video keyframes! Here are your custom captions:",
                        "captions": generated_captions
                    })

                    # 🟢 Smart Cleanup: Only delete old videos, NOT the currently active one
                    if "video_path" in last_msg and os.path.exists(last_msg["video_path"]):
                        if st.session_state.active_video != last_msg["video_path"]:
                            try:
                                os.remove(last_msg["video_path"])
                            except Exception:
                                pass

            except Exception as e:
                if 'loading_placeholder' in locals():
                    loading_placeholder.empty()
                error_msg = f"An issue occurred during the execution pipeline: `{str(e)}`"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})