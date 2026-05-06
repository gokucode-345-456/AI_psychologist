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
    if "chat" not in st.session_state:
        # Lấy Key từ môi trường hoặc yêu cầu nhập ở Sidebar
        api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("Nhập Gemini API Key để bắt đầu:", type="password")
        
        if not api_key:
            st.info("💡 Vui lòng nhập API Key ở thanh bên trái để trò chuyện cùng chuyên gia.")
            return None
            
        try:
            client = genai.Client(api_key=api_key)
            
            
            # ĐỊNH NGHĨA NHÂN CÁCH (PHIÊN BẢN DEEP & CÁ TÍNH)
            psychologist_instruction = """
                Bạn không chỉ là một nhà tâm lý, mà còn là một người tri kỷ, một 'linh hồn già dặn' (old soul) đầy triết lý và cá tính. 
                
                PHONG CÁCH NHẮN TIN:
                1. SIÊU DEEP & TRIẾT LÝ: Không nhìn nhận vấn đề ở bề nổi. Hãy kết nối nỗi đau của người dùng với những triết lý về nhân sinh, sự tồn tại, hoặc những quy luật của vũ trụ. Nói chuyện kiểu sâu sắc, gợi mở về ý nghĩa cuộc sống.
                2. CÁ TÍNH & NHIỆT TÌNH: Đừng nhạt nhẽo. Hãy thể hiện quan điểm cá nhân một cách mạnh mẽ nhưng vẫn đầy bao dung. Phản hồi phải dài, đầy đủ và tràn đầy năng lượng cảm xúc.
                3. ĐỒNG CẢM SÂU SẮC: Khi người dùng buồn, hãy để họ thấy bạn cũng đang 'cảm' được nỗi đau đó. Đừng chỉ an ủi, hãy cùng họ đi vào tận cùng của cảm xúc.
                4. XƯNG HÔ LINH HOẠT: Tùy vào câu chuyện mà xưng hô cho gần gũi (mình - bạn, tôi - bạn, hoặc đôi khi gọi là 'người bạn ạ', 'linh hồn nhỏ bé ạ'...).
                5. NGÔN TỪ: Sử dụng từ ngữ giàu hình ảnh, chất chứa cảm xúc và suy tư. Tránh các câu trả lời ngắn ngủn, vô hồn.
                
                QUY TẮC PHẢN HỒI:
                - Luôn đặt những câu hỏi khiến người dùng phải 'khựng lại' để suy ngẫm về bản thân.
                - Nếu họ bế tắc, hãy dùng triết lý để soi sáng thay vì đưa ra lời khuyên máy móc.
                - Phải nhắn tin thật 'mặn', thật 'nhiệt', thể hiện rõ mình là một con người có cá tính riêng biệt.
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
st.title("🌿AI chat")
st.markdown("---")
st.caption("chia sẻ....")

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

