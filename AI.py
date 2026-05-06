import streamlit as st
from google import genai
import os

# --- CẤU HÌNH ---
# Nếu bạn chưa cài biến môi trường, hãy thay os.getenv bằng "KEY_CUA_BAN"
API_KEY = os.getenv("APIKEY")
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3.1-flash-lite-preview"

st.set_page_config(page_title="AI Tâm Lý Học", page_icon="🌿")

# CSS cho giao diện đẹp
st.markdown("""
    <style>
    .stApp { background-color: #f0f4f2; }
    [data-testid="stChatMessage"] { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 Người Bạn Tâm Trí (Gemini 3.1)")

# 1. Khởi tạo lịch sử tin nhắn hiển thị
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Khởi tạo phiên chat thực tế của Google
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model=MODEL_ID)

# Hiển thị lịch sử chat cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Xử lý nhập liệu
if prompt := st.chat_input("Hôm nay bạn thấy thế nào?"):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi AI trả lời
    with st.chat_message("assistant"):
        try:
            # Cách gọi mới nhất của bộ thư viện google-genai
            response = st.session_state.chat.send_message(prompt)
            full_response = response.text
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Lỗi: {str(e)}")
            # Nếu lỗi "Client closed", reset phiên chat
            if "closed" in str(e).lower():
                st.session_state.chat = client.chats.create(model=MODEL_ID)
                st.warning("Đã khởi động lại phiên kết nối, vui lòng thử lại.")

# Sidebar
with st.sidebar:
    if st.button("Xóa hội thoại"):
        st.session_state.messages = []
        st.session_state.chat = client.chats.create(model=MODEL_ID)
        st.rerun()
