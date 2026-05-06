import streamlit as st
from google import genai
import os
import json

# --- 1. CẤU HÌNH GIAO DIỆN & ÉP HIỆN SIDEBAR ---
st.set_page_config(
    page_title="AI Soulmate", 
    page_icon="🌙", 
    layout="centered",
    initial_sidebar_state="expanded" # Ép bung sidebar ngay từ khi load
)

# CSS "QUYỀN LỰC": KHÔNG CHO SIDEBAR ẨN
st.markdown("""
    <style>
    /* Nền đen toàn app */
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }

    /* ÉP SIDEBAR PHẢI HIỆN (Dù ông có lỡ tay đóng) */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #222;
        min-width: 300px !important;
        margin-left: 0px !important;
    }

    /* Hiển thị rõ cái nút mở (mũi tên >) để ông thấy nó ở đâu */
    [data-testid="collapsedControl"] {
        display: block !important;
        top: 10px !important;
        left: 10px !important;
        background-color: white !important; /* Cho nó màu trắng cho dễ nhìn */
        border-radius: 50%;
    }

    /* Nút bấm màu trắng trong sidebar */
    div.stSidebar div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
        border: none;
        height: 3em;
    }
    
    /* Ô nhập liệu và Chat */
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    .stChatInput textarea { background-color: #1A1A1A !important; color: #FFFFFF !important; }
    
    /* Làm sáng các Tab đăng ký/đăng nhập */
    button[data-baseweb="tab"] { color: white !important; }
    div[data-baseweb="tab-highlight"] { background-color: white !important; }

    [data-testid="stToolbar"], footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. QUẢN LÝ TÀI KHOẢN ---
USER_DB = "users_db.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB, "w") as f: json.dump(users, f)

def load_user_history(username):
    path = f"history_{username}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return []

def save_user_history(username, messages):
    with open(f"history_{username}.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# --- 3. GIAO DIỆN SIDEBAR ---
with st.sidebar:
    st.title("🌙 Soulmate Portal")
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        tab_login, tab_signup = st.tabs(["Đăng nhập", "Đăng ký"])
        
        with tab_signup:
            new_user = st.text_input("Tên định danh:", key="reg_user")
            new_pass = st.text_input("Mật mã:", type="password", key="reg_pass")
            if st.button("Xác nhận đăng ký"):
                if new_user and new_pass:
                    save_user(new_user, new_pass)
                    st.success("Đã đăng ký!")
                else: st.error("Thiếu thông tin.")

        with tab_login:
            user_n = st.text_input("Tên đăng nhập:", key="log_user")
            pass_w = st.text_input("Mật mã:", type="password", key="log_pass")
            if st.button("Vào thế giới tri kỷ"):
                users = load_users()
                if user_n in users and users[user_n] == pass_w:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_n
                    st.rerun()
                else: st.error("Sai thông tin rồi.")
    else:
        st.write(f"👤 Bạn là: **{st.session_state.current_user}**")
        if st.button("➕ Cuộc trò chuyện mới"):
            st.session_state.messages = []
            save_user_history(st.session_state.current_user, [])
            st.rerun()
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

# --- 4. CHÍNH DIỆN ---
if st.session_state.logged_in:
    user = st.session_state.current_user
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = load_user_history(user)

    st.title(f"🌙 Tri kỷ của {user}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Nói gì đi..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        API_KEY = os.getenv("APIKEY")
        if API_KEY:
            try:
                client = genai.Client(api_key=API_KEY)
                chat = client.chats.create(
                    model="gemini-3.1-flash-lite-preview",
                    config={"system_instruction": "bạn là một học sinh cấp 3 năng động và đầy cá tính, bạn có khả năng đồng cảm người khác, có thể deeptalk nếu người dùng hạ giọng xuống, bạn là 1 người rất an ủi và quan tânm người khác, nhắn tin giống như gen z"},
                    history=[{"role": "user" if m["role"]=="user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages[:-1]]
                )
                res = chat.send_message(prompt)
                with st.chat_message("assistant"): st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                save_user_history(user, st.session_state.messages)
            except Exception as e: st.error(f"Lỗi: {e}")
        else: st.error("Thiếu API Key!")
else:
    st.info("🌙 Hãy đăng ký hoặc đăng nhập ở thanh bên trái để bắt đầu.")
