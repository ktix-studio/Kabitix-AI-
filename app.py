import streamlit as st
from logo import show_logo
from welcome import welcome_cards
from utils import apply_theme

# --- LAZY IMPORTS (fast loading) ---
@st.cache_resource
def get_modules():
    from chatbot import get_ai_response, speech_to_text
    from vision import analyze_image
    from pdf_reader import read_pdf
    from word_reader import read_word
    from excel_reader import read_excel
    from image_generator import generate_image
    from voice_reply import speak
    return get_ai_response, speech_to_text, analyze_image, read_pdf, read_word, read_excel, generate_image, speak

get_ai_response, speech_to_text, analyze_image, read_pdf, read_word, read_excel, generate_image, speak = get_modules()

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Kabitix AI - All in One AI", page_icon="🤖", layout="centered")
apply_theme()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# =========================
# SIDEBAR - PRO LEVEL
# =========================
st.sidebar.title("🤖 Kabitix AI")
st.sidebar.caption("Your All-in-One AI")

if st.sidebar.button("🏠 Home", use_container_width=True):
    st.session_state.page = "🏠 Home"
    st.rerun()

if st.sidebar.button("🤖 Chat", use_container_width=True):
    st.session_state.page = "🤖 Chat"
    st.rerun()

if st.sidebar.button("➕ New Chat", use_container_width=True):
    if st.session_state.messages:
        st.session_state.history.append(st.session_state.messages.copy())
    st.session_state.messages = []
    st.session_state.pdf_context = ""
    st.rerun()

with st.sidebar.expander("📜 History", expanded=True):
    for i, chat in enumerate(st.session_state.history):
        title = chat[0]["content"][:25] + "..." if chat else f"Chat {i+1}"
        if st.button(f"💬 {title}", key=f"h_{i}", use_container_width=True):
            st.session_state.messages = chat
            st.session_state.page = "🤖 Chat"
            st.rerun()

if st.sidebar.button("🗑️ Clear History"):
    st.session_state.history = []
    st.rerun()

# =========================
# HOME
# =========================
if st.session_state.page == "🏠 Home":
    show_logo()
    welcome_cards()
    st.info("👈 Select 🤖 Chat from sidebar to start!")
    st.stop()

# =========================
# CHAT PAGE
# =========================
st.title("🤖 Kabitix AI")
st.caption("Chat • Read Docs • Generate Images • Vision")

# --- Tools in clean tabs ---
tab1, tab2, tab3 = st.tabs(["📄 Documents", "📷 Vision", "🎨 Generate Image"])

with tab1:
    colA, colB = st.columns(2)
    with colA:
        pdf = st.file_uploader("PDF", type=["pdf"])
        if pdf:
            st.session_state.pdf_context = read_pdf(pdf)
            st.success("PDF loaded!")
    with colB:
        word = st.file_uploader("Word", type=["docx"])
        if word:
            st.session_state.pdf_context = read_word(word)
            st.success("Word loaded!")

    excel = st.file_uploader("Excel", type=["xlsx","xls"])
    if excel:
        try:
            txt = read_excel(excel)
            st.session_state.pdf_context += "\n" + txt
            st.success("Excel loaded!")
        except Exception as e:
            st.error(e)

with tab2:
    img = st.file_uploader("Upload image", type=["png","jpg","jpeg"], key="vision")
    if img:
        st.image(img, use_container_width=True)
        q = st.text_input("Ask about image")
        if st.button("🔍 Analyze"):
            with st.spinner("Analyzing..."):
                res = analyze_image(img, q)
            st.markdown(res)

with tab3:
    prompt_img = st.text_input("Describe image you want")
    if st.button("🎨 Generate"):
        if not prompt_img.strip():
            st.warning("Write description!")
        else:
            with st.spinner("Generating..."):
                im = generate_image(prompt_img)
            if im:
                st.image(im, use_container_width=True)
            else:
                st.error("Failed, check API key in Render")

# --- Chat messages (ONLY ONCE) ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- Chat Input ---
from streamlit_mic_recorder import mic_recorder
col1, col2 = st.columns([0.85, 0.15])
prompt = None

with col1:
    txt = st.chat_input("Ask anything...")
    if txt:
        prompt = txt

with col2:
    voice = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", just_once=True, key="mic")
    if voice:
        with open("voice.wav","wb") as f:
            f.write(voice["bytes"])
        try:
            prompt = speech_to_text("voice.wav")
        except Exception as e:
            st.error(f"Voice error: {e}")

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Kabitix thinking..."):
            try:
                reply = get_ai_response(prompt, st.session_state.pdf_context)
            except Exception as e:
                reply = f"❌ Error: {e}"
        st.markdown(reply)
        try:
            audio = speak(reply)
            if audio:
                st.audio(audio)
        except:
            pass
    st.session_state.messages.append({"role":"assistant","content":reply}) 
