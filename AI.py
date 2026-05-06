import streamlit as st
from google import genai
import os
import json
import streamlit.components.v1 as components

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="AI Soulmate", 
    page_icon="🌙", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS & JS "TUYỆT CHIÊU CUỐI": NHẤN LÀ BUNG
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }

    /* LÀM NỔI BẬT NÚT MỞ GỐC */
    [data-testid="collapsedControl"] {
        background-color: #FFFFFF !important;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        top: 15px !important;
        left: 15px !important;
        display: flex !important;
        z-index: 999999 !important;
        box-shadow: 0 0 20px rgba(255,255,255,0.6) !important;
        cursor: pointer !important;
    }
    
    [data-testid="collapsedControl"] svg {
        fill: #000000 !important;
        width: 30px !important;
        height: 30px !important;
    }

    /* Sidebar & Chat */
    section[data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #222; }
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    [data-testid="stToolbar"], footer, header { visibility: hidden; }
    
    /* Nút bắt đầu giữa màn hình */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        padding: 10px 25px !important;
        border: none !important;
    }
    </style>

    <script>
    // JS để ép mở Sidebar khi người dùng nhấn vào nút hoặc vùng điều khiển
    function openSidebar() {
        const sidebarButton = window.parent.document.querySelector('button[kind="headerNoPadding"]');
        if (sidebarButton) {
            sidebarButton.click();
        }
    }
    // Lắng nghe sự kiện click trên toàn bộ document của Streamlit
    window.parent.document.addEventListener('click', function(e) {
        // Nếu nhấn vào cái vùng nút trắng ở góc
        if (e.target.closest('[data-testid="collapsedControl"]')) {
            openSidebar();
        }
    });
    </script>
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
                    st.success("Đã đăng ký thành công!")
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
        st.write(f"👤 Chào mừng, **{st.session_state.current_user}**")
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

# --- 4. MAIN CONTENT ---
if st.session_state.logged_in:
    user = st.session_state.current_user
    st.title(f"🌙 Tri kỷ của {user}")
    
    if "messages" not in st.session_state:
        st.session_state.messages = load_user_history(user)

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Nhắn gì đó đi..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun() # Hoặc gọi AI ở đây
else:
    # MÀN HÌNH CHỜ
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="font-size: 3rem;">🌙 AI Soulmate</h1>
            <p style="font-size: 1.2rem; opacity: 0.8;">Cậu ơi, nhấn vào nút trắng ở góc trái hoặc nút dưới đây để bắt đầu nhé.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Nút bấm trung tâm để ép rerun (Streamlit sẽ tự bung sidebar vì state mặc định là expanded)
    if st.button("✨ MỞ ĐĂNG NHẬP", use_container_width=True):
        st.rerun()
