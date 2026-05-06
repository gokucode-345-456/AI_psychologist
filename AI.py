import streamlit as st
from google import genai
import os

# 1. Cấu hình trang - Hiển thị đẹp hơn trên trình duyệt
st.set_page_config(page_title="AI Tâm Lý", page_icon="🌿", layout="centered")

# 2. Quản lý API Key
# Ưu tiên lấy từ biến môi trường hệ thống (An toàn, không lo bị lộ Key)
API_KEY_ENV = os.getenv("APIKEY")

def get_chat_session():
    """Khởi tạo hoặc lấy lại phiên chat hiện tại"""
    if "chat" not in st.session_state:
        # Nếu không có Key trong môi trường, yêu cầu nhập ở Sidebar
        api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("Nhập Gemini API Key:", type="password")
        
        if not api_key:
            st.warning("Vui lòng cấu hình API Key để bắt đầu trò chuyện.")
            return None
            
        try:
            client = genai.Client(api_key=api_key)
            # Sử dụng Gemini 3.1 Flash Lite Preview theo ý bạn
            # Nếu bản này lỗi, có thể đổi về "gemini-1.5-flash"
            model_id = "gemini-3.1-flash-lite-preview" 
            
            st.session_state.chat = client.chats.create(model=model_id)
            st.session_state.client_instance = client
            st.sidebar.success(f"Đang dùng: {model_id}")
        except Exception as e:
            st.error(f"Lỗi khởi tạo AI: {e}")
            return None
    return st.session_state.chat

# 3. Khởi tạo bộ nhớ tin nhắn
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- GIAO DIỆN ---
st.title("🌿 Người Bạn Tâm Trí")
st.caption("Lắng nghe và chia sẻ cùng bạn mọi lúc.")

# Hiển thị lịch sử chat từ bộ nhớ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Xử lý nhập liệu từ người dùng
if prompt := st.chat_input("Hôm nay bạn thấy thế nào?"):
    # Hiển thị tin nhắn của User ngay lập tức
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Lưu vào lịch sử để không bị mất khi Streamlit rerun
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Lấy phiên chat và gửi tin nhắn cho AI
    chat = get_chat_session()
    if chat:
        with st.chat_message("assistant"):
            try:
                # Gửi tin nhắn và nhận phản hồi
                response = chat.send_message(prompt)
                ai_reply = response.text
                
                st.markdown(ai_reply)
                # Lưu phản hồi AI vào lịch sử
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"AI không trả lời được: {e}")
                # Nếu lỗi do Client bị đóng, xóa session để khởi tạo lại ở lần tới
                if "closed" in str(e).lower():
                    del st.session_state.chat

# Tùy chọn xóa hội thoại ở Sidebar
with st.sidebar:
    st.divider()
    if st.button("Xóa lịch sử trò chuyện"):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        st.rerun()
