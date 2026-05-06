import streamlit as st
from google import genai
import os
import json

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="AI Soulmate", 
    page_icon="🌙", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS FIX TRIỆT ĐỂ: HIỆN NÚT SIDEBAR & NÚT TRUNG TÂM
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }

    /* HIỆN NÚT GÓC TRÁI (Bất chấp mọi thứ) */
    [data-testid="collapsedControl"] {
        background-color: #FFFFFF !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        top: 15px !important;
        left: 15px !important;
        display: flex !important;
        z-index: 999999 !important; /* Đẩy lên lớp cao nhất */
        box-shadow: 0 0 15px rgba(255,255,255,0.8) !important;
    }
    
    [data-testid="collapsedControl"] svg {
        fill: #000000 !important;
    }

    /* CSS CHO CÁI NÚT CHÍNH GIỮA MÀN HÌNH */
    .main-login-btn {
        background-color: #FFFFFF;
        color: #000000 !important;
        padding: 15px 30px;
        border-radius: 30px;
        font-weight: bold;
        text-decoration: none;
        font-size: 1.2rem;
        transition: 0.3s;
        border: none;
        cursor: pointer;
        box-shadow: 0 5px 15px rgba(255,255,255,0.2);
    }
    .main-login-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 5px 25px rgba(255,255,255,0.4);
    }

    /* Sidebar & Chat */
    section[data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #222; }
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    [data-testid="stToolbar"], footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. QUẢN LÝ TÀI KHOẢN (GIỮ NGUYÊN) ---
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

# --- 3. SIDEBAR LOGIC ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.title("🌙 Soulmate Portal")
    if not st.session_state.logged_in:
        tab_login, tab_signup = st.tabs(["Đăng nhập", "Đăng ký"])
        with tab_signup:
            new_user = st.text_input("Tên định danh:", key="reg_user")
            new_pass = st.text_input("Mật mã:", type="password", key="reg_pass")
            if st.button("Xác nhận đăng ký"):
                if new_user and new_pass:
                    save_user(new_user, new_pass)
                    st.success("Xong rồi! Qua đăng nhập nhé.")
        with tab_login:
            user_n = st.text_input("Tên đăng nhập:", key="log_user")
            pass_w = st.text_input("Mật mã:", type="password", key="log_pass")
            if st.button("Vào thế giới tri kỷ", key="sidebar_login_btn"):
                users = load_users()
                if user_n in users and users[user_n] == pass_w:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_n
                    st.rerun()
                else: st.error("Sai thông tin rồi nè.")
    else:
        st.write(f"👤 Chào cậu, **{st.session_state.current_user}**")
        if st.button("➕ Chat mới"):
            st.session_state.messages = []
            save_user_history(st.session_state.current_user, [])
            st.rerun()
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

# --- 4. MAIN CONTENT ---
if st.session_state.logged_in:
    user = st.session_state.current_user
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = load_user_history(user)
    
    st.title(f"🌙 Tri kỷ của {user}")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Nhắn gì đó với tớ đi..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        # Logic AI ở đây...
else:
    # MÀN HÌNH CHỜ VỚI NÚT BẤM GIỮA MÀN HÌNH
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="font-size: 3.5rem;">🌙 Chào cậu, tớ là AI Soulmate</h1>
            <p style="font-size: 1.3rem; opacity: 0.8; margin-bottom: 40px;">
                Tớ ở đây để lắng nghe và chia sẻ cùng cậu mọi lúc.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tạo cái nút bằng Streamlit nhưng "giả dạng" HTML để điều hướng vào sidebar
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✨ BẮT ĐẦU NGAY", use_container_width=True):
            # Trick: Khi bấm nút này, ta ép sidebar hiện ra nếu nó đang ẩn
            st.info("Nhìn sang bên trái để Đăng nhập nhé! ←")
            # Streamlit không có lệnh code để tự mở sidebar, 
            # nhưng nút này sẽ kích hoạt rerun và sidebar sẽ hiện theo state mặc định
            st.rerun()

    st.markdown("""
        <div style="text-align: center; margin-top: 30px; opacity: 0.6;">
            <p>Hoặc nhấn vào dấu <b>></b> ở góc trái phía trên nếu nút không hiện</p>
        </div>
    """, unsafe_allow_html=True)
