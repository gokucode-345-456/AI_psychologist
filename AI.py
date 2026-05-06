import streamlit as st
from google import genai
import os

# 1. Cấu hình trang
st.set_page_config(page_title="AI Tâm Lý", page_icon="🌿")

# 2. Kiểm tra API Key (Đảm bảo không bị crash ở đây)
MY_API_KEY = APIKEY

def get_chat_session():
    if "chat" not in st.session_state:
        try:
            client = genai.Client(api_key=MY_API_KEY)
            # Khởi tạo chat với bản ổn định trước để test
            st.session_state.chat = client.chats.create(model="gemini-1.5-flash")
            st.session_state.client_instance = client
        except Exception as e:
            st.error(f"Lỗi khởi tạo AI: {e}")
            return None
    return st.session_state.chat

# 3. Khởi tạo lịch sử
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- GIAO DIỆN ---
st.title("🌿 Người Bạn Tâm Trí")

# Hiển thị lịch sử cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Xử lý nhập liệu
if prompt := st.chat_input("Hôm nay bạn thấy thế nào?"):
    # Hiển thị tin nhắn User
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Gọi AI
    chat = get_chat_session()
    if chat:
        with st.chat_message("assistant"):
            try:
                response = chat.send_message(prompt)
                ai_reply = response.text
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"AI không trả lời được: {e}")
