import streamlit as st
from google import genai
import os

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="AI chat", 
    page_icon="🌿", 
    layout="centered"
)

# Thêm một chút CSS để giao diện mềm mại hơn
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. QUẢN LÝ API KEY ---
API_KEY_ENV = os.getenv("APIKEY")

def get_chat_session():
    """Khởi tạo phiên chat với nhân cách Nhà Tâm Lý Học"""
    if "chat" not in st.session_state:
        # Lấy Key từ môi trường hoặc yêu cầu nhập ở Sidebar
        api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("Nhập Gemini API Key để bắt đầu:", type="password")
        
        if not api_key:
            st.info("💡 Vui lòng nhập API Key ở thanh bên trái để trò chuyện cùng chuyên gia.")
            return None
            
        try:
            client = genai.Client(api_key=api_key)
            
            # ĐỊNH NGHĨA NHÂN CÁCH (SYSTEM INSTRUCTION)
            psychologist_instruction = """
            Bạn là một nhà tâm lý học lâm sàng thấu cảm, ấm áp và kiên nhẫn. 
            Phong cách trò chuyện của bạn:
            - Luôn lắng nghe chân thành, không phán xét.
            - Sử dụng các kỹ thuật như phản hồi cảm xúc ("Mình nghe thấy sự lo lắng trong lời kể của bạn...")
            - Đặt câu hỏi gợi mở để người dùng tự thấu hiểu bản thân.
            - Tuyệt đối không đưa ra lời khuyên máy móc kiểu "Bạn nên làm thế này".
            - Ngôn ngữ tiếng Việt nhẹ nhàng, xưng "Mình" và "Bạn".
            - Nếu người dùng có ý định tự hại, hãy nhẹ nhàng khuyên họ liên hệ hotline hỗ trợ tâm lý hoặc cơ sở y tế gần nhất
            _ nhắn tin cảm xúc nhiều hơn đi
            _nhắn tin cũng phải có 1 tí cá tính nghen 
            _vừa cá tính mà vừa đồng cảm với người khác
            """

            # Khởi tạo phiên chat với cấu hình nhân cách
            st.session_state.chat = client.chats.create(
                model="gemini-3.1-flash-lite-preview",
                config={
                    "system_instruction": psychologist_instruction,
                    "temperature": 0.7, # Tăng độ sáng tạo và cảm xúc
                }
            )
            st.session_state.client_instance = client
        except Exception as e:
            st.error(f"Lỗi khởi tạo: {e}")
            return None
    return st.session_state.chat

# --- 3. KHỞI TẠO BỘ NHỚ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🌿 Nhà Tâm Lý Trị Liệu AI")
st.markdown("---")
st.caption("Chào bạn, mình luôn ở đây để lắng nghe những tâm tư của bạn mà không phán xét.")

# Hiển thị lịch sử trò chuyện
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. XỬ LÝ TIN NHẮN ---
if prompt := st.chat_input("Hôm nay bạn cảm thấy thế nào?"):
    # Hiển thị tin nhắn User
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Gọi AI trả lời
    chat = get_chat_session()
    if chat:
        with st.chat_message("assistant"):
            try:
                response = chat.send_message(prompt)
                ai_reply = response.text
                
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"⚠️ Có lỗi xảy ra: {e}")
                if "closed" in str(e).lower():
                    del st.session_state.chat

# --- 6. SIDEBAR TÙY CHỌN ---
with st.sidebar:
    st.header("Cấu hình")
    if st.button("🗑️ Xóa cuộc hội thoại"):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        st.rerun()
    
    st.divider()
    st.write("📌 **Lưu ý:** AI không thể thay thế hoàn toàn chuyên gia y tế trong các trường hợp khẩn cấp.")
