import streamlit as st
from google import genai
import os

client = genai.Client(api_key=os.getenv("APIKEY"))

st.title("🌿 AI Psychologist")

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model="gemini-1.5-pro",
        config={
            "system_instruction": "Bạn là chuyên gia tâm lý nhẹ nhàng, không phán xét."
        }
    )

if prompt := st.chat_input("Nói đi..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        res = st.session_state.chat.send_message(prompt)
        st.markdown(res.text)
