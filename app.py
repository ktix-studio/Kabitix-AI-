import streamlit as st
from chatbot import get_ai_response, speech_to_text 
from study import study_page
from ebook import ebook_page
from translator import translator_page
from settings import settings_page
from logo import show_logo
from welcome import welcome_cards
from utils import apply_theme
from vision import analyze_image
from streamlit_mic_recorder import mic_recorder 
from pdf_reader import read_pdf 
from voice_reply import speak  
from image_generator import generate_image 
from word_reader import read_word 
from excel_reader import read_excel 
st.set_page_config(
    page_title="Kabitix ",
    page_icon="🤖",
    layout="centered" 
)

apply_theme()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home" 


if st.session_state.page == "🏠 Home":
    show_logo()
    welcome_cards()
    st.stop() 

page = st.session_state.page

if page == "📚 AI Study":
    study_page()
    st.stop()

elif page == "📚 eBook Creator":
    ebook_page()
    st.stop()

elif page == "🌍 Translator":
    translator_page()
    st.stop()

elif page == "⚙️ Settings":
    settings_page()
    st.stop()

st.sidebar.title("🤖 Kabitix ")
import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = [] 
if st.sidebar.button("➕ New Chat"):
    if st.session_state.messages:
        st.session_state.history.append(
            st.session_state.messages.copy()
        )
    st.session_state.messages = []
    st.rerun()

with st.sidebar.expander("📜 History", expanded=True):
    for i, chat in enumerate(st.session_state.history):
        title = (
            chat[0]["content"][:20] + "..."
            if chat else f"Chat {i+1}"
        )

        if st.button(
            f"💬 {title}",
            key=f"history_{i}"
        ):
            st.session_state.messages = chat
            st.rerun()

if st.sidebar.button("🗑️ Clear History"):
    st.session_state.history = []
    st.rerun() 
if st.session_state.page == "🤖 Chat":
    st.title("🤖 Kabitix")
    st.caption("How can I help you today?") 
with st.expander("📎 Tools"): 
   uploaded_pdf = st.file_uploader(
    "📄 Upload PDF",
    type=["pdf"],
    key="pdf_upload"
) 

pdf_text = ""

if uploaded_pdf:
    pdf_text = read_pdf(uploaded_pdf)
    st.success("✅ PDF uploaded successfully!") 
uploaded_word = st.file_uploader(
    "📄 Upload Word File",
    type=["docx"],
    key="word_upload"
)

if uploaded_word:
    pdf_text = read_word(uploaded_word)
    st.success("✅ Word file uploaded successfully!") 
uploaded_image = st.file_uploader(
    "📷 Upload an image",
    type=["png", "jpg", "jpeg"],
    key="main_image_upload"
)

if uploaded_image:
    st.image(uploaded_image, use_container_width=True)

    image_question = st.text_input(
        "Ask something about this image"
    )

    if st.button("🔍 Analyze Image"):

        with st.spinner("🤖 Analyzing image..."):

            result = analyze_image(
                uploaded_image,
                image_question
            )

        st.success("Analysis Complete!")
        st.markdown(result)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) 
prompt = None 
voice = mic_recorder(
    start_prompt="🎤 Speak",
    stop_prompt="⏹ Stop",
    key="mic"
)
if voice:
    with open("voice.wav", "wb") as f:
        f.write(voice["bytes"])

    prompt = speech_to_text("voice.wav")

    st.success(f"🎤 You said: {prompt}") 
    show_image = st.button("🎨 Image Generator") 
if show_image: 
    image_prompt = st.text_input( 
    "Describe the image you want to create"
)

if st.button("🎨 Generate Image"):
      with st.spinner("Generating image..."):
        image = generate_image(image_prompt)
        if image:
        st.image(image)
    else:
        st.error("Image generation failed. Check Render logs.") 
text_prompt = st.chat_input("💬 Ask anything...")

if text_prompt:
    prompt = text_prompt 

if prompt:

    st.session_state.messages.append(
    {
        "role": "user",
        "content": prompt
    }
)

with st.chat_message("user"):
    st.markdown(prompt)

with st.chat_message("assistant"):

    with st.spinner("🤖 Kabitix is thinking..."): 
        reply = get_ai_response(prompt, pdf_text)

    audio_file = speak(reply)
    st.audio(audio_file)

    st.markdown(reply)

st.session_state.messages.append(
    {
        "role": "assistant",
        "content": reply
    }
) 
