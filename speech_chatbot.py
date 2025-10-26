# =====================================
# SPEECH-ENABLED CHATBOT (CLOUD READY + UI ENHANCED)
# =====================================

import streamlit as st
import nltk
import random
import speech_recognition as sr
import tempfile

# NLTK setup
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

# --------------------------------------
# 1️⃣ Load and preprocess corpus
# --------------------------------------
@st.cache_data
def load_corpus(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        corpus = f.read()
    return corpus

corpus = load_corpus('human_chat.txt')

# --------------------------------------
# 2️⃣ Extract conversational pairs
# --------------------------------------
def extract_pairs(corpus_text):
    pairs = []
    lines = corpus_text.split("\n")
    for i in range(len(lines) - 1):
        if lines[i].startswith("Human 1:") and lines[i + 1].startswith("Human 2:"):
            q = lines[i].replace("Human 1:", "").strip()
            a = lines[i + 1].replace("Human 2:", "").strip()
            pairs.append((q, a))
    return pairs

pairs = extract_pairs(corpus)

# --------------------------------------
# 3️⃣ Chatbot Response Logic
# --------------------------------------
bot_greeting = [
    'Hello User! Do you have any questions?',
    'Hey there! What can I help you with?',
    'I am like a genie in a bottle. Hit me with your question.',
    'Hi! How can I help you today?'
]

bot_farewell = [
    'Thanks for chatting. Goodbye!',
    'I hope you had a good experience!',
    'Have a great day ahead!',
    'Bye for now!'
]

human_greeting = ['hi', 'hello', 'hey', 'good day', 'hola']
human_exit = ['thank you', 'thanks', 'bye', 'goodbye', 'quit']

def chatbot_response(user_input):
    user_input = user_input.lower()
    if any(g in user_input for g in human_greeting):
        return random.choice(bot_greeting)
    if any(e in user_input for e in human_exit):
        return random.choice(bot_farewell)
    for q, a in pairs:
        if any(word in user_input for word in q.lower().split()):
            return a
    return "Hmm, I’m not sure I understand that. Could you please rephrase?"

# --------------------------------------
# 4️⃣ Offline-friendly Speech Recognition
# --------------------------------------
def transcribe_audio_file(uploaded_file):
    recognizer = sr.Recognizer()
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_audio_path = temp_audio.name
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        st.error(f"❌ Speech recognition failed: {e}")
        return None

# --------------------------------------
# 5️⃣ Streamlit UI
# --------------------------------------
st.set_page_config(page_title="Speech Chatbot", page_icon="🗣️", layout="centered")

st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712100.png",
    width=120,
)
st.markdown(
    """
    <h1 style='text-align: center; color: #4B8BBE;'>🎙️ Speech-Enabled Chatbot</h1>
    <p style='text-align: center;'>Interact by typing or uploading your voice (WAV format)</p>
    """,
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["💬 Text Chat", "🎧 Voice Chat"])

with tab1:
    st.subheader("💬 Type your message")
    user_text = st.text_input("Say something...")
    if st.button("Send Text"):
        if user_text.strip():
            response = chatbot_response(user_text)
            st.success(f"🤖 Chatbot: {response}")
        else:
            st.warning("Please type a message first.")

with tab2:
    st.subheader("🎧 Upload your voice message (WAV only)")
    uploaded_audio = st.file_uploader("Upload Audio File", type=["wav"])
    if uploaded_audio is not None:
        st.audio(uploaded_audio, format='audio/wav')
        if st.button("Transcribe & Chat"):
            text = transcribe_audio_file(uploaded_audio)
            if text:
                st.info(f"🗣️ You said: **{text}**")
                response = chatbot_response(text)
                st.success(f"🤖 Chatbot: {response}")
