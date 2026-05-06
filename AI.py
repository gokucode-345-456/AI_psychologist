import streamlit as st
from google import genai
import os

# --- HÀM KHỞI TẠO CLIENT ---
def get_client():
    if "client" not in st.session_state:
        # Lấy API Key
        api_key = os.getenv("APIKEY")
        # Lưu client vào session_state để không bị đóng
        st.session_state.client = genai.Client(api_key=api_key)
    return st.session_state.client

# --- KHỞI TẠO PHIÊN CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    client = get_client()
    st.session_state.chat = client.chats.create(model="gemini-3.1-flash-lite-preview")

# --- PHẦN XỬ LÝ TIN NHẮN ---
if prompt := st.chat_input("Hôm nay bạn thấy thế nào?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Luôn dùng chat từ session_state
            response = st.session_state.chat.send_message(prompt)
            full_response = response.text
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            # Nếu vẫn bị lỗi đóng client, ta ép tạo mới
            st.error("Kết nối bị ngắt, đang thử kết nối lại...")
            del st.session_state.client
            del st.session_state.chat
            st.rerun()
