import streamlit as st
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

from tools.stt import transcribe_audio
from tools.intent import classify_intent
from tools.executor import execute

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Voice AI Agent", layout="wide")

st.markdown("""
<style>
    /* Styling Streamlit Main App */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: linear-gradient(-45deg, #000000, #001f3f, #000000, #001f3f);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Input widgets container styling */
    div.stSelectbox > div > div, .stTextArea textarea, .stFileUploader {
        border-radius: 10px !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
        color: #ffffff !important;
    }
    
    /* Buttons */
    div.stButton > button {
        border-radius: 8px !important;
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        font-weight: 500 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.2s ease;
        backdrop-filter: blur(5px);
    }
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.3) !important;
        transform: scale(1.02);
    }

    /* Alerts and Expander Cards */
    .stAlert {
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255,255,255,0.15);
        background-color: rgba(255,255,255,0.05);
    }
    
    /* Sidebar styling for glassmorphism look */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 15, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Typography */
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: -0.5px;
        color: #ffffff !important;
    }
    p, label, span, div.stMarkdown p {
        color: #f0f0f0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("MINI GRAVITY")

if "history" not in st.session_state:
    st.session_state.history = []
if "pending_intents" not in st.session_state:
    st.session_state.pending_intents = []
if "current_text" not in st.session_state:
    st.session_state.current_text = ""
if "uploaded_file_path" not in st.session_state:
    st.session_state.uploaded_file_path = None

with st.sidebar:
    st.header("Session History")
    for idx, item in enumerate(st.session_state.history):
        st.markdown(f"**Input:** {item['input']}")
        st.markdown(f"**Result:** {item['result']}")
        
        res_str = str(item['result'])
        if "code written to" in res_str:
            file_path = res_str.split("code written to ")[-1].strip()
            if os.path.exists(file_path):
                prog_input = st.text_input("Program Input (Optional):", key=f"prog_input_{idx}", help="Data to pass to input() function")
                if st.button("▶️ Run Program", key=f"run_btn_{idx}"):
                    import subprocess
                    st.info(f"Running `{os.path.basename(file_path)}`...")
                    try:
                        cmd_input = prog_input + "\n" if prog_input else None
                        proc = subprocess.run([sys.executable, file_path], input=cmd_input, capture_output=True, text=True, timeout=5)
                        if proc.stdout:
                            st.success("Output:")
                            st.code(proc.stdout)
                        if proc.stderr:
                            st.error("Errors:")
                            st.code(proc.stderr)
                    except subprocess.TimeoutExpired:
                        st.warning("Execution timed out. Make sure the script doesn't require interactive `input()` from the terminal.")
                    except Exception as e:
                        st.error(f"Failed to run: {e}")
                        
        st.markdown("---")

input_type = st.selectbox(
    "Choose Input Type",
    ["Text", "Audio", "File"]
)

user_text=None
audio_file=None
uploaded_file=None
file_cmd_audio=None   # audio command used in File mode

if input_type=="Text":
    user_text=st.text_area("Enter your command")
elif input_type=="Audio":
    audio_file = st.audio_input("Record Voice Command")
    if not audio_file:
        audio_file = st.file_uploader("Or upload an existing audio file", type=["wav", "mp3", "m4a", "ogg"])
elif input_type=="File":
    uploaded_file = st.file_uploader("📄 Upload document (PDF, DOCX, XLSX, PPTX, TXT)")
    st.markdown("**How do you want to give your command?**")
    cmd_tab1, cmd_tab2, cmd_tab3 = st.tabs(["⌨️ Type", "🎙️ Record Voice", "📁 Upload Audio"])
    with cmd_tab1:
        user_text = st.text_area("Enter your command for the document", key="file_cmd_text")
    with cmd_tab2:
        file_cmd_audio = st.audio_input("Record your command", key="file_cmd_live")
    with cmd_tab3:
        file_cmd_audio = file_cmd_audio or st.file_uploader(
            "Upload audio command", type=["wav","mp3","m4a","ogg"], key="file_cmd_upload"
        )

# Function to run the app
if st.button("Run"):
    text = ""
    # 🔹 FILE MODE
    if input_type == "File":
        if not uploaded_file:
            st.warning("Please upload a document first.")
            st.stop()

        # Save the uploaded document
        file_path = os.path.join(BASE_DIR, "output", uploaded_file.name)
        os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state.uploaded_file_path = file_path

        # Resolve the command — typed text takes priority, then audio
        if user_text and user_text.strip():
            text = user_text.strip()
        elif file_cmd_audio is not None:
            try:
                audio_path = os.path.join(BASE_DIR, "input", file_cmd_audio.name)
                os.makedirs(os.path.join(BASE_DIR, "input"), exist_ok=True)
                with open(audio_path, "wb") as f:
                    f.write(file_cmd_audio.read())
                st.info("Transcribing voice command...")
                text = transcribe_audio(audio_path)
                st.success(f"Transcription: {text}")
            except Exception as e:
                st.error(f"Failed to transcribe audio command: {e}")
                st.stop()
        else:
            st.warning("Please type or record a command for the document.")
            st.stop()

    # 🔹 TEXT MODE
    elif input_type == "Text":
        if not user_text:
            st.warning("Enter text")
            st.stop()
        text = user_text

    # 🔹 AUDIO MODE
    elif input_type == "Audio":
        if audio_file is None:
            st.error("Please upload an audio file")
            st.stop()
        try:
            file_path = os.path.join(BASE_DIR, "input", audio_file.name)
            os.makedirs(os.path.join(BASE_DIR, "input"), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(audio_file.read())
            st.info("Transcribing audio...")
            text = transcribe_audio(file_path)
            st.success(f"Transcription: {text}")
        except Exception as e:
            st.error(f"Failed to transcribe audio: {e}")
            st.stop()

    if text:
        st.info("Detecting intent...")
        try:
            # Context-aware classification
            context_file = os.path.basename(st.session_state.uploaded_file_path) if st.session_state.uploaded_file_path else None
            intents = classify_intent(text, context_file=context_file)
            
            if isinstance(intents, dict):
                intents = [intents]
            
            # Inject active file path into ALL intents for contextual awareness
            if st.session_state.uploaded_file_path:
                for intent in intents:
                    if "details" not in intent:
                        intent["details"] = {}
                    # Only inject if filename is empty or refers to the context file
                    details = intent["details"]
                    detected_file = str(details.get("filename", "")).lower()
                    if not detected_file or detected_file in ["this file", "the document", "it", str(context_file).lower()]:
                        intent["details"]["file_path"] = st.session_state.uploaded_file_path

            st.session_state.pending_intents = intents
            st.session_state.current_text = text
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to detect intent: {e}")
            st.stop()

st.markdown("---")

if st.session_state.pending_intents:
    intent_data = st.session_state.pending_intents[0]
    intent_name = intent_data.get("intent", "unknown")
    
    st.subheader(f"Next Action: {intent_name}")
    st.json(intent_data)
    
    unsafe_intents = ["create_file", "write_code", "delete_file", "rename_file", "modify_file", "repair_file"]
    
    if intent_name in unsafe_intents:
        st.warning(f"This action ({intent_name}) will modify files. Do you want to proceed?")
        col1, col2 = st.columns(2)
        if col1.button("✅ Approve"):
            try:
                with st.spinner("Executing..."):
                    result = execute(intent_data)
                st.success(f"Done: {result}")
                st.session_state.history.append({"input": st.session_state.current_text, "result": result})
            except Exception as e:
                st.error(f"Execution Error: {e}")
                st.session_state.history.append({"input": st.session_state.current_text, "result": f"Error: {e}"})
            st.session_state.pending_intents.pop(0)
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.experimental_rerun()
            
        if col2.button("❌ Reject"):
            st.warning("Action rejected by user.")
            st.session_state.history.append({"input": st.session_state.current_text, "result": "Action rejected"})
            st.session_state.pending_intents.pop(0)
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.experimental_rerun()
    else:
        # Auto-run safe intents
        try:
            with st.spinner("Executing safe action..."):
                result = execute(intent_data)
            st.success(f"Done: {result}")
            st.session_state.history.append({"input": st.session_state.current_text, "result": result})
        except Exception as e:
            st.error(f"Execution Error: {e}")
            st.session_state.history.append({"input": st.session_state.current_text, "result": f"Error: {e}"})
        st.session_state.pending_intents.pop(0)
        
        if st.session_state.pending_intents:
            if st.button("Next Action"):
                if hasattr(st, "rerun"):
                    st.rerun()
                else:
                    st.experimental_rerun()
        else:
            st.success("All actions completed.")