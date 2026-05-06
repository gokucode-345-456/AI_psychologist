import streamlit as st
from google import genai
import os

client = genai.Client(api_key=os.getenv("APIKEY"))

# --- TRƯỚC ĐÓ: genai.configure(api_key="...") ---

# Dùng hàm này để đảm bảo client luôn sống
def get_chat_session():
    if "chat" not in st.session_state:
        # Khởi tạo model
        model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
        # Khởi tạo phiên chat và lưu vào session_state
        st.session_state.chat = model.start_chat(history=[])
    return st.session_state.chat

# --- TRONG PHẦN XỬ LÝ TIN NHẮN ---
if prompt := st.chat_input("Hôm nay bạn thấy thế nào?"):
    # Hiển thị tin nhắn user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi AI trả lời
    with st.chat_message("assistant"):
        chat_session = get_chat_session() # Gọi hàm này thay vì dùng trực tiếp
        try:
            response = chat_session.send_message(prompt)
            full_response = response.text
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Lỗi kết nối: {str(e)}")
            # Nếu client chết, xóa đi để lần sau nó tự tạo mới
            if "chat" in st.session_state:
                del st.session_state.chat
