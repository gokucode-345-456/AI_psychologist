import streamlit as st
from google import genai
import os

st.set_page_config(page_title="AI Psychologist", page_icon="🌿")
st.title("🌿 AI Psychologist")

client = genai.Client(api_key=os.getenv("APIKEY"))

# init chat
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model="gemini-1.5-pro",
        config={
            "system_instruction": "Bạn là một chuyên gia tâm lý học nhẹ nhàng, không phán xét."
        }
    )
    st.session_state.messages = []

# render chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input
if prompt := st.chat_input("Hôm nay bạn thấy sao?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        res = st.session_state.chat.send_message(prompt)
        reply = res.text
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
