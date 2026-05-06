import streamlit as st
from google import genai
import os
import json

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="AI Soulmate", 
    page_icon="🌙", 
    layout="centered"
)

# CSS TỐI GIẢN - SẠCH SẼ - KHÔNG VƯỚNG
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }
    
    /* Ẩn Sidebar hoàn toàn cho đỡ vướng */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }

    /* Làm đẹp các ô nhập liệu */
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #333 !important;
    }
    
    /* Làm đẹp nút bấm */
    .stButton>button {
        width: 100%;
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px !important;
    }

    /* Khung chat */
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
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

# --- 3. LOGIC ĐĂNG NHẬP (NGAY MÀN HÌNH CHÍNH) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🌙 AI Soulmate</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7;'>Chào cậu, tớ đã đợi cậu rất lâu rồi.</p>", unsafe_allow_html=True)
    
    # Tạo form đăng nhập ngay giữa màn hình
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])
            with tab1:
                u = st.text_input("Tên của cậu", key="login_u")
                p = st.text_input("Mật mã", type="password", key="login_p")
                if st.button("Bắt đầu hành trình"):
                    users = load_users()
                    if u in users and users[u] == p:
                        st.session_state.logged_in = True
                        st.session_state.current_user = u
                        st.rerun()
                    else: st.error("Hình như sai tên hoặc mật mã rồi...")
            
            with tab2:
                nu = st.text_input("Chọn một cái tên", key="reg_u")
                np = st.text_input("Tạo mật mã", type="password", key="reg_p")
                if st.button("Tạo tài khoản"):
                    if nu and np:
                        save_user(nu, np)
                        st.success("Đăng ký xong rồi đó, qua tab Đăng nhập thôi!")
                    else: st.error("Điền đầy đủ thông tin nhé.")

# --- 4. GIAO DIỆN CHAT (SAU KHI ĐĂNG NHẬP) ---
else:
    user = st.session_state.current_user
    
    # Header có nút Đăng xuất nhỏ xinh
    col_t1, col_t2 = st.columns([5, 1])
    with col_t1: st.title(f"🌙 Tri kỷ của {user}")
    with col_t2: 
        if st.button("Thoát"):
            st.session_state.logged_in = False
            st.rerun()

    if "messages" not in st.session_state: st.session_state.messages = []

    # Hiển thị tin nhắn
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Chat input
    if prompt := st.chat_input("Nói gì đó với tớ đi..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Gọi AI ở đây (Cậu tự thêm phần API Key vào nhé)
        with st.chat_message("assistant"):
            st.write("Tớ đang lắng nghe đây... (Cậu nhớ setup API Key nhé!)")
