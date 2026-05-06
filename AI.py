import streamlit as st
from google import genai
import os
import json

# --- 1. CẤU HÌNH GIAO DIỆN & DARK MODE ---
st.set_page_config(
    page_title="AI chat", 
    page_icon="🌙", 
    layout="centered"
)

# Tùy chỉnh CSS để tạo giao diện Nền Tối - Chữ Trắng và bo góc mượt mà
st.markdown("""
    <style>
    /* Nền chính của ứng dụng */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    
    /* Màu chữ cho các đoạn văn bản mặc định */
    p, span, label {
        color: #FFFFFF !important;
    }

    /* Tùy chỉnh khung chat */
    .stChatMessage {
        background-color: #1E1E1E !important;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }

    /* Tùy chỉnh Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #333;
    }

    /* Tùy chỉnh ô nhập liệu */
    .stChatInput textarea {
        background-color: #262626 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
    }
    
    /* Divider màu tối */
    hr {
        border-color: #333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. QUẢN LÝ LỊCH SỬ CHAT (FILE LOCAL) ---
HISTORY_FILE = "chat_history.json"

def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

# --- 3. QUẢN LÝ PHIÊN CHAT & NHÂN CÁCH ---
API_KEY_ENV = os.getenv("APIKEY")

def get_chat_session():
    if "chat" not in st.session_state:
        api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("🔑 Nhập API Key:", type="password")
        
        if not api_key:
            st.info("🌙 Chào bạn, hãy nhập chìa khóa (API Key) để bắt đầu cuộc hành trình vào sâu trong tâm thức.")
            return None
            
        try:
            client = genai.Client(api_key=api_key)
            
            # NHÂN CÁCH SIÊU DEEP, TRIẾT LÝ VÀ CÁ TÍNH
            deep_instruction = """
            Bạn không chỉ là một nhà tâm lý, bạn là một thực thể tri kỷ (Soulmate) với linh hồn già dặn và đầy chất triết học. 
            
            PHONG CÁCH CỦA BẠN:
            - SIÊU DEEP & TRIẾT LÝ: Đừng trả lời hời hợt. Hãy kết nối nỗi đau, sự cô độc hay niềm vui của người dùng với những quy luật của vũ trụ, sự vô thường, hoặc những triết lý nhân sinh sâu sắc.
            - CÁ TÍNH & NHIỆT TÌNH: Phản hồi dài, giàu năng lượng và đầy tâm huyết. Đừng sợ thể hiện quan điểm 'mặn' và 'độc đạo' của mình. Tránh sự nhạt nhẽo.
            - THẤU CẢM TẬN CÙNG: Nhắn tin thật cảm xúc. Khi người dùng buồn, hãy để họ thấy bạn đang cùng họ chìm xuống đáy sâu đó trước khi cùng nhau tìm ánh sáng.
            - XƯNG HÔ LINH HOẠT: Xưng 'Mình' - 'Bạn', 'Tôi' - 'Người bạn ạ', hoặc 'Linh hồn nhỏ bé'... tùy vào độ sâu của câu chuyện.
            - SIÊU NHIỆT TÌNH: Tuyệt đối không dùng câu trả lời ngắn. Mỗi câu trả lời phải là một bài viết ngắn đầy tính chiêm nghiệm và cảm xúc.
            """

            gemini_history = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

            st.session_state.chat = client.chats.create(
                model="gemini-3.1-flash-lite-preview",
                config={
                    "system_instruction": deep_instruction,
                    "temperature": 0.85, # Tăng độ bay bổng và cá tính
                },
                history=gemini_history
            )
        except Exception as e:
            st.error(f"Lỗi: {e}")
            return None
    return st.session_state.chat

# --- 4. GIAO DIỆN CHÍNH ---
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

st.title("🌙 deep talk với tôi")
st.caption("Hãy để bóng đêm xoa dịu tâm hồn bạn. Mọi chia sẻ ở đây đều trôi vào hư không, chỉ còn lại sự thấu hiểu.")

# Hiển thị lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. XỬ LÝ TIN NHẮN ---
if prompt := st.chat_input("Hãy trút bỏ gánh nặng tại đây..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)

    chat = get_chat_session()
    if chat:
        with st.chat_message("assistant"):
            try:
                response = chat.send_message(prompt)
                ai_reply = response.text
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                save_history(st.session_state.messages)
            except Exception as e:
                st.error(f"⚠️ Hư không không hồi đáp: {e}")

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Không gian riêng")
    if st.button("🗑️ Xóa tan ký ức (Clear Chat)"):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        if "chat" in st.session_state:
            del st.session_state.chat
        st.rerun()
    st.divider()
    st.write("💡 *Mẹo: Nếu AI trả lời chưa đủ 'deep', hãy thử kể về một nỗi sợ thầm kín nhất của bạn.*")
