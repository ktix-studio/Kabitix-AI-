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


# =========================
# PAGE CONFIGURATION
# =========================

st.set_page_config(
    page_title="Kabitix",
    page_icon="🤖",
    layout="centered"
)

apply_theme()


# =========================
# SESSION STATE
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"


# =========================
# HOME PAGE
# =========================

if st.session_state.page == "🏠 Home":

    show_logo()
    welcome_cards()

    st.stop()


# =========================
# OTHER PAGES
# =========================

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


# =========================
# SIDEBAR
# =========================

st.sidebar.title("🤖 Kabitix")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "🏠 Home"
    st.rerun()


if st.sidebar.button("➕ New Chat"):

    if st.session_state.messages:
        st.session_state.history.append(
            st.session_state.messages.copy()
        )

    st.session_state.messages = []

    st.rerun()


# =========================
# CHAT HISTORY
# =========================

with st.sidebar.expander("📜 History", expanded=True):

    for i, chat in enumerate(st.session_state.history):

        title = (
            chat[0]["content"][:20] + "..."
            if chat
            else f"Chat {i + 1}"
        )

        if st.button(
            f"💬 {title}",
            key=f"history_{i}"
        ):

            st.session_state.messages = chat
            st.session_state.page = "🤖 Chat"

            st.rerun()


if st.sidebar.button("🗑️ Clear History"):

    st.session_state.history = []

    st.rerun()


# =========================
# CHAT PAGE
# =========================

st.title("🤖 Kabitix")
st.caption("How can I help you today?")


# =========================
# TOOLS
# =========================

with st.expander("📎 Tools"):

    # -------- PDF --------

    uploaded_pdf = st.file_uploader(
        "📄 Upload PDF",
        type=["pdf"],
        key="pdf_upload"
    )

    pdf_text = ""

    if uploaded_pdf:

        pdf_text = read_pdf(uploaded_pdf)

        st.success("✅ PDF uploaded successfully!")


    # -------- WORD --------

    uploaded_word = st.file_uploader(
        "📄 Upload Word File",
        type=["docx"],
        key="word_upload"
    )

    if uploaded_word:

        pdf_text = read_word(uploaded_word)

        st.success("✅ Word file uploaded successfully!")


    # -------- EXCEL --------

    uploaded_excel = st.file_uploader(
        "📊 Upload Excel File",
        type=["xlsx", "xls"],
        key="excel_upload"
    )

    if uploaded_excel:

        try:

            excel_text = read_excel(uploaded_excel)

            st.success("✅ Excel file uploaded successfully!")

            if excel_text:
                pdf_text += "\n\n" + excel_text

        except Exception as e:

            st.error(f"❌ Excel reading failed: {e}")


    # -------- IMAGE --------

    uploaded_image = st.file_uploader(
        "📷 Upload an image",
        type=["png", "jpg", "jpeg"],
        key="main_image_upload"
    )

    if uploaded_image:

        st.image(
            uploaded_image,
            use_container_width=True
        )

        image_question = st.text_input(
            "Ask something about this image",
            key="image_question"
        )

        if st.button("🔍 Analyze Image"):

            with st.spinner("🤖 Analyzing image..."):

                result = analyze_image(
                    uploaded_image,
                    image_question
                )

            st.success("✅ Analysis Complete!")

            st.markdown(result)


# =========================
# IMAGE GENERATOR
# =========================

st.markdown("### 🎨 Image Generator")

image_prompt = st.text_input(
    "Describe the image you want to create",
    key="image_prompt"
)

if st.button("🎨 Generate Image"):

    if not image_prompt.strip():

        st.warning("Please describe the image first.")

    else:

        with st.spinner("🤖 Generating image..."):

            image = generate_image(image_prompt)

        if image:

            st.image(
                image,
                use_container_width=True
            )

        else:

            st.error(
                "❌ Image generation failed. Check Render logs."
            )


# =========================
# SHOW PREVIOUS MESSAGES
# =========================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# =========================
# CHAT INPUT WITH MIC
# =========================

prompt = None

# Create two columns: text input (wide) + mic (small)
col1, col2 = st.columns([0.85, 0.15])

with col1:
    text_input = st.text_input(
        "Ask anything...",
        key="text_chat",
        label_visibility="collapsed",
        placeholder="💬 Ask anything..."
    )
    if text_input.strip():
        prompt = text_input

with col2:
    voice = mic_recorder(
        start_prompt="🎤",
        stop_prompt="",
        just_once=False,
        key="voice_recorder"
    )
    if voice:
        try:
            with open("voice.wav", "wb") as f:
                f.write(voice["bytes"])
            prompt = speech_to_text("voice.wav")
        except Exception as e:
            st.error(f"Voice error: {e}")

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# AI Response
if prompt:
    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI response
    with st.chat_message("assistant"):
        with st.spinner("🤖 Kabitix is thinking..."):
            try:
                reply = get_ai_response(prompt, pdf_text)
            except Exception as e:
                reply = f"❌ Error: {e}"
        
        st.markdown(reply)
        
        # Voice reply
        try:
            audio_file = speak(reply)
            if audio_file:
                st.audio(audio_file)
        except:
            pass
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    }) 
        
