import streamlit as st
from google import genai
import os

# 1. Cấu hình trang (Phải để ở đầu)
st.set_page_config(page_title="AI Tâm Lý", page_icon="🌿")

# 2. Hàm lấy Client (Tránh lỗi Closed Client)
def get_client():
    if "client" not in st.session_state:
        # Thay bằng Key thật của bạn
        api_key = os.getenv("APIKEY")
        st.session_state.client = genai.Client(api_key=api_key)
    return st.session_state.client

# 3. Khởi tạo các biến lưu trữ trong bộ nhớ
if "messages" not in st.session_state:
    st.session_state.messages = []  # Lưu để hiển thị lên màn hình

if "chat" not in st.session_state:
    client = get_client()
    # Khởi tạo phiên chat với model 3.1
    st.session_state.chat = client.chats.create(model="gemini-3.1-flash-lite-preview")

# --- GIAO DIỆN ---
st.title("🌿 Người Bạn Tâm Trí")

# 4. QUAN TRỌNG: Hiển thị lại toàn bộ tin nhắn cũ mỗi khi web load lại
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Xử lý khi người dùng gửi tin nhắn mới
if prompt := st.chat_input("Chia sẻ với mình nhé..."):
    # BƯỚC A: Hiển thị ngay tin nhắn của bạn lên màn hình
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # BƯỚC B: Lưu vào bộ nhớ (để lần sau load lại không bị mất)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # BƯỚC C: Gọi AI trả lời
    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(prompt)
            ai_reply = response.text
            st.markdown(ai_reply)
            
            # Lưu câu trả lời của AI vào bộ nhớ
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        except Exception as e:
            st.error("Kết nối bị gián đoạn. Đang khởi động lại...")
            # Nếu lỗi, xóa client cũ để Streamlit tạo lại cái mới ở lần chạy sau
            del st.session_state.client
            del st.session_state.chat
            st.rerun()
