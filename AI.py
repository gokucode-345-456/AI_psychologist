import streamlit as st
from google import genai
import os

client = genai.Client(api_key=os.getenv("APIKEY"))

st.title("🌿 AI Psychologist")

# lưu messages thôi
if "messages" not in st.session_state:
    st.session_state.messages = []

# hiển thị chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input
if prompt := st.chat_input("Hôm nay bạn thấy sao?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # gọi AI mỗi lần (KHÔNG dùng chat object cũ)
    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[
                {"role": "user", "parts": [m["content"]]}
                for m in st.session_state.messages
            ]
        )

        reply = response.text
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
