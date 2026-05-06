import streamlit as st
from google import genai
import os
import json

# --- 1. CẤU HÌNH GIAO DIỆN & KHÓA SIDEBAR ---
st.set_page_config(
    page_title="AI chat", 
    page_icon="🌙", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS FIX LỖI TÀNG HÌNH CHỮ
st.markdown("""
    <style>
    /* Nền đen tổng thể */
    .stApp {
        background-color: #000000 !important;
    }

    /* CHỈ ÉP CHỮ TRẮNG CHO VĂN BẢN CHAT VÀ TIÊU ĐỀ */
    .stMarkdown p, .stMarkdown li, .stMarkdown span, h1, h2, h3 {
        color: #FFFFFF !important;
    }

    /* GIỮ NGUYÊN MÀU CHO CODE BLOCK (KHÔNG BỊ TÀNG HÌNH) */
    code {
        color: #f8f8f2 !important; /* Màu xám sáng cho code */
        background-color: #272822 !important; /* Nền tối cho code block */
        padding: 2px 4px;
        border-radius: 4px;
    }
    
    /* FIX Sidebar: Chữ trong sidebar cũng phải trắng */
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }

    /* KHÓA SIDEBAR */
    [data-testid="collapsedControl"] { display: none !important; }
    button[title="Collapse sidebar"] { display: none !important; }
    
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #222;
    }

    /* STYLE NÚT TRẮNG */
    div.stSidebar div.stButton > button:first-child {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        height: 3.5em;
    }

    /* Khung chat */
    .stChatMessage {
        background-color: #161616 !important;
        border: 1px solid #333 !important;
    }

    /* Ô NHẬP LIỆU */
    [data-testid="stChatInput"] { background-color: #000000 !important; }
    [data-testid="stChatInput"] div[role="presentation"] { background-color: transparent !important; }
    
    .stChatInput textarea {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 1px solid #444 !important;
    }

    /* Ẩn rác */
    [data-testid="stToolbar"] {display: none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. QUẢN LÝ LỊCH SỬ ---
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

# --- 3. HÀM GỬI TIN NHẮN (GEMINI 3.1) ---
def send_to_ai(prompt):
    api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("🔑 API Key:", type="password")
    if not api_key:
        st.info("🌙 Hãy nhập API Key để bắt đầu.")
        return None

    try:
        client = genai.Client(api_key=api_key)
        instruction = "Bạn là một thực thể tri kỷ deep, triết lý. Xưng hô Mình - Bạn. Trả lời rõ ràng, trắng sáng."
        
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
        st.error(f"⚠️ Hư không lỗi: {e}")
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.write("") 
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.write("") 
    if st.button("🗑️ Xóa tan ký ức", use_container_width=True):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
        st.rerun()
