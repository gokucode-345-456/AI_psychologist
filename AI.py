import streamlit as st
from google import genai
import os

# --- 1. CẤU HÌNH GIAO DIỆN & KHÓA SIDEBAR ---
st.set_page_config(
    page_title="AI chat", 
    page_icon="🌙", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS TỔNG LỰC: CHỐNG TÀNG HÌNH, ĐEN TUYỀN, NÚT TRẮNG
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    
    /* Chữ trắng rõ nét cho toàn bộ văn bản */
    p, span, label, li, h1, h2, h3, .stMarkdown {
        color: #FFFFFF !important;
    }

    /* Khối code đen tiệp màu nền */
    code, pre, [data-testid="stCodeBlock"] {
        background-color: #111111 !important; 
        color: #eeeeee !important;
        border: 1px solid #333 !important;
    }
    
    /* Khóa Sidebar không cho ẩn */
    [data-testid="collapsedControl"] { display: none !important; }
    button[title="Collapse sidebar"] { display: none !important; }
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #222;
    }

    /* Nút "Cuộc trò chuyện mới" màu trắng */
    div.stSidebar div.stButton > button:first-child {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        height: 3.5em;
    }

    /* Khung chat và Ô nhập liệu */
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    [data-testid="stChatInput"] { background-color: #000000 !important; }
    .stChatInput textarea { background-color: #1A1A1A !important; color: #FFFFFF !important; border: 1px solid #333 !important; }

    /* Ẩn rác giao diện */
    [data-testid="stToolbar"] {display: none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. QUẢN LÝ LỊCH SỬ (SESSION ONLY - KHÔNG DÙNG FILE JSON ĐỂ TRÁNH LỘ CHAT) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

API_KEY_ENV = os.getenv("APIKEY")

# --- 3. HÀM GỬI TIN NHẮN (GEMINI 3.1 FLASH LITE) ---
def send_to_ai(prompt):
    api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("🔑 API Key:", type="password")
    if not api_key:
        st.info("🌙 Hãy nhập API Key ở bên trái.")
        return None

    try:
        client = genai.Client(api_key=api_key)
        instruction = "Bạn là tri kỷ deep. Xưng hô Mình - Bạn. Phản hồi sâu sắc, ngắn gọn."
        
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
        st.error(f"⚠️ Lỗi: {e}")
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

    with st.chat_message("assistant"):
        ai_reply = send_to_ai(prompt)
        if ai_reply:
            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# --- 5. SIDEBAR ---
with st.sidebar:
    st.write("") 
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.messages = [] # Xóa sạch session hiện tại
        st.rerun()

    st.write("") 
    if st.button("🗑️ Xóa tan ký ức", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Chat này chỉ mình bạn thấy trong phiên làm việc này.")
