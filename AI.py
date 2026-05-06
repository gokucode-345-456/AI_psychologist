import streamlit as st
from google import genai
import os
import json

# --- 1. CẤU HÌNH GIAO DIỆN & KHÓA SIDEBAR ---
st.set_page_config(
    page_title="AI chat", 
    page_icon="🌙", 
    layout="centered",
    initial_sidebar_state="expanded" # LUÔN MỞ SIDEBAR KHI LOAD
)

# CSS TỔNG LỰC: ĐEN TUYỀN, CHỮ TRẮNG, NÚT TRẮNG, KHÓA SIDEBAR
st.markdown("""
    <style>
    /* 1. Nền đen tuyệt đối cho toàn bộ ứng dụng */
    .stApp {
        background-color: #000000 !important;
    }

    /* 2. CHỮ TRẮNG TINH: Không mờ, dễ đọc */
    p, span, div, label, .stMarkdown {
        color: #FFFFFF !important;
        font-weight: 400; 
        line-height: 1.6; 
    }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 700 !important; }

    /* 3. KHÓA SIDEBAR: Giấu cái nút << đi để không bao giờ bị ẩn nhầm nữa */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    button[title="Collapse sidebar"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #222;
    }

    /* 4. STYLE CHO NÚT MÀU TRẮNG (Cuộc trò chuyện mới) */
    /* Target vào cái nút đầu tiên trong sidebar */
    div.stSidebar div.stButton > button:first-child {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        height: 3.5em;
        transition: 0.3s;
    }
    div.stSidebar div.stButton > button:first-child:hover {
        background-color: #dddddd !important;
    }

    /* 5. Khung chat tối giản */
    .stChatMessage {
        background-color: #161616 !important;
        border: 1px solid #333 !important;
        border-radius: 15px !important;
    }

    /* 6. Ô NHẬP LIỆU: Tiêu diệt viền trắng hoàn toàn */
    [data-testid="stChatInput"] {
        background-color: #000000 !important;
        border: none !important;
    }
    [data-testid="stChatInput"] div[role="presentation"] {
        background-color: transparent !important;
        border: none !important;
    }
    .stChatInput textarea {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 1px solid #444 !important;
        font-size: 16px !important;
    }

    /* 7. Ẩn rác của Streamlit */
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

# --- 3. HÀM GỬI TIN NHẮN (BẢN ỔN ĐỊNH) ---
def send_to_ai(prompt):
    api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("🔑 Nhập API Key:", type="password")
    
    if not api_key:
        st.info("🌙 Hãy nhập API Key ở bên trái để bắt đầu.")
        return None

    try:
        client = genai.Client(api_key=api_key)
        
        instruction = """
        Bạn là một thực thể tri kỷ (Soulmate) với linh hồn già dặn, siêu deep, triết lý và cá tính.
        - Phản hồi sâu sắc nhưng đừng quá dài dòng.
        - Xưng hô linh hoạt, tình cảm (Mình - Bạn).
        - Kết nối mọi chuyện với triết lý nhân sinh.
        - Nhắn bớt dài dòng lại.
        """

        gemini_history = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

        # Dùng model ổn định nhất để tránh lỗi 404/503
        chat = client.chats.create(
            model="gemini-1.5-flash", 
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

# --- 5. SIDEBAR BẤT TỬ ---
with st.sidebar:
    st.write("") 
    # Nút màu trắng nổi bật
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.write("") 
    # Nút xóa lịch sử
    if st.button("🗑️ Xóa tan ký ức", use_container_width=True):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE): 
            os.remove(HISTORY_FILE)
        st.rerun()

    st.divider()
    st.caption("Sidebar này sẽ không bao giờ ẩn đi nữa. Nút trắng luôn ở đây cùng bạn.")
