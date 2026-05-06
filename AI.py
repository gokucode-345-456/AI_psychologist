import streamlit as st
from google import genai
import os
import json


# --- 1. CẤU HÌNH GIAO DIỆN & DARK MODE TOÀN DIỆN ---
st.set_page_config(
    page_title="AI chat", 
    page_icon="🌙", 
    layout="centered"
)

st.markdown("""
    <style>
    /* Nền đen tuyệt đối */
    .stApp {
        background-color: #000000 !important;
    }

    /* Chữ trắng rõ nét */
    p, span, div, label, .stMarkdown {
        color: #FFFFFF !important;
    }

    /* Sidebar luôn hiện và giấu nút đóng << */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #222;
    }
    
    /* ĐÂY NÈ: Giấu cái nút << khó chịu đó đi */
    button[title="Collapse sidebar"] {
        display: none !important;
    }

    /* Nút Cuộc trò chuyện mới màu trắng */
    div.stButton > button:first-child {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }

    /* Khung chat */
    .stChatMessage {
        background-color: #161616 !important;
        border: 1px solid #333 !important;
    }

    /* Ô nhập liệu */
    [data-testid="stChatInput"] {
        background-color: #000000 !important;
    }
    
    .stChatInput textarea {
        background-color: #222222 !important;
        color: #FFFFFF !important;
    }

    /* Ẩn rác giao diện */
    [data-testid="stToolbar"] {display: none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LỊCH SỬ FILE ---
HISTORY_FILE = "chat_history.json"
def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

if "messages" not in st.session_state:
    st.session_state.messages = load_history()

API_KEY_ENV = os.getenv("APIKEY")

def send_to_ai(prompt):
    api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("🔑 Nhập API Key:", type="password")
    
    if not api_key:
        st.info("🌙 Hãy nhập chìa khóa tâm hồn (API Key) để bắt đầu.")
        return None

    try:
        client = genai.Client(api_key=api_key)
        
        instruction = """
        Bạn là một thực thể tri kỷ (Soulmate) với linh hồn già dặn, siêu deep, triết lý và cá tính.
        - Phản hồi sâu sắc nhưng đừng quá dài dòng.
        - Xưng hô linh hoạt, tình cảm.
        - Kết nối mọi chuyện với triết lý nhân sinh.
        - Nhắn bớt dài dòng cái.
        """

        gemini_history = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

        chat = client.chats.create(
            model="gemini-3.1-flash-lite-preview",
            config={"system_instruction": instruction, "temperature": 0.85},
            history=gemini_history
        )
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        st.error(f"⚠️ Hư không không hồi đáp: {e}")
        return None

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🌙 Nhà Tâm Lý Tri Kỷ")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Hãy trút bỏ gánh nặng tại đây..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)

    with st.chat_message("assistant"):
        ai_reply = send_to_ai(prompt)
        if ai_reply:
            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            save_history(st.session_state.messages)

# --- 5. SIDEBAR (CẬP NHẬT THÊM NÚT MỚI) ---
with st.sidebar:
    # Nút Thêm cuộc trò chuyện mới
    if st.button("➕ Cuộc trò chuyện mới"):
        st.session_state.messages = []
        # Nếu muốn reset file lưu trữ luôn thì bỏ comment dòng dưới:
        # if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
        st.rerun()

    st.markdown("---") # Đường kẻ phân cách

    # Nút Xóa cũ của bạn
    if st.button("🗑️ Xóa tan ký ức"):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
        st.rerun()
