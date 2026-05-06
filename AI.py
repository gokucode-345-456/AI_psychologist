import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH GOOGLE GEMINI ---
genai.configure(api_key="AIzaSyDEn5F9GJubODx_JfpL8JvuBDDjRP2mpSE")

# Cấu hình model với chỉ dẫn về tâm lý học (System Instruction)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Bạn là một chuyên gia tâm lý học thân thiện, lắng nghe và không phán xét. Hãy sử dụng ngôn ngữ nhẹ nhàng, gợi mở và giúp người dùng gọi tên cảm xúc của họ."
)

# --- THIẾT KẾ GIAO DIỆN CSS ---
st.set_page_config(page_title="AI Tâm Lý Học", page_icon="🌿")


st.markdown("""
    <style>
    /* Màu nền tổng thể nhẹ nhàng */
    .stApp {
        background-color: #f0f4f2;
    }
    
    /* Tùy chỉnh khung chat */
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    /* Bong bóng chat của AI */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Bong bóng chat của Người dùng */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #e3f2fd;
    }

    /* Tiêu đề */
    h1 {
        color: #2e7d32;
        font-family: 'Helvetica Neue', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GIAO DIỆN ỨNG DỤNG ---
st.title("🌿 AI PSYCHOLOGIST")
st.caption("chat đi")

# Khởi tạo bộ nhớ chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị các tin nhắn cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý nhập liệu từ người dùng
if prompt := st.chat_input("Hôm nay bạn cảm thấy thế nào?"):
    # Hiển thị tin nhắn người dùng  
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi AI trả lời
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Gửi toàn bộ lịch sử để AI có ngữ cảnh
        chat_session = model.start_chat(
            history=[
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ]
        )
        
        response = chat_session.send_message(prompt)
        full_response = response.text
        
        message_placeholder.markdown(full_response)
    
    # Lưu câu trả lời của AI
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- SIDEBAR THÔNG TIN ---
with st.sidebar:
    st.header("Lưu ý")
    if st.button("Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()