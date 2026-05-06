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

# CSS: ĐEN TUYỀN, NÚT TRẮNG, KHÓA SIDEBAR
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #222; }
    
    /* Nút trắng cho toàn bộ sidebar */
    div.stSidebar div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
        border: none;
    }
    
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    .stChatInput textarea { background-color: #1A1A1A !important; color: #FFFFFF !important; }
    [data-testid="stToolbar"], footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HÀM QUẢN LÝ TÀI KHOẢN & LỊCH SỬ ---
USER_DB = "users_db.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB, "w") as f: json.dump(users, f)

def get_history_file(username):
    return f"history_{username}.json"

def save_user_history(username, messages):
    with open(get_history_file(username), "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_user_history(username):
    file_path = get_history_file(username)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    return []

# --- 3. SIDEBAR: ĐĂNG KÝ & ĐĂNG NHẬP ---
with st.sidebar:
    st.title("🌙 Soulmate Portal")
    
    # Tạo 2 tab trong Sidebar
    tab_login, tab_signup = st.tabs(["Đăng nhập", "Đăng ký"])
    
    logged_in_user = None

    with tab_signup:
        new_user = st.text_input("Tạo tên định danh:", key="reg_user")
        new_pass = st.text_input("Tạo mật mã:", type="password", key="reg_pass")
        if st.button("Xác nhận đăng ký"):
            users = load_users()
            if new_user in users:
                st.warning("Tên này có chủ rồi ông ơi!")
            elif new_user and new_pass:
                save_user(new_user, new_pass)
                st.success("Đăng ký xong! Qua tab Đăng nhập đi.")
            else:
                st.error("Đừng để trống ô nào nhé.")

    with tab_login:
        user_name = st.text_input("Tên định danh:", key="log_user")
        pass_word = st.text_input("Mật mã:", type="password", key="log_pass")
        users = load_users()
        if st.button("Vào thế giới tri kỷ"):
            if user_name in users and users[user_name] == pass_word:
                st.session_state.logged_in = True
                st.session_state.current_user = user_name
                st.success(f"Đã mở khóa tâm hồn cho {user_name}")
                st.rerun()
            else:
                st.error("Sai tên hoặc mật mã rồi.")

    st.divider()
    
    # Nút chức năng khi đã đăng nhập
    if st.session_state.get("logged_in"):
        if st.button("➕ Cuộc trò chuyện mới"):
            st.session_state.messages = []
            save_user_history(st.session_state.current_user, [])
            st.rerun()
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

# --- 4. GIAO DIỆN CHAT ---
if st.session_state.get("logged_in"):
    user = st.session_state.current_user
    
    # Chỉ load lịch sử 1 lần khi vừa đăng nhập
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = load_user_history(user)

    st.title(f"🌙 Tri kỷ của {user}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Trút bầu tâm sự..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        API_KEY = os.getenv("APIKEY")
        if not API_KEY:
            st.error("Quên chưa cài API Key rồi ông chủ ơi!")
        else:
            try:
                client = genai.Client(api_key=API_KEY)
                chat = client.chats.create(
                    model="gemini-3.1-flash-lite-preview",
                    config={"system_instruction": "Bạn là tri kỷ deep. Xưng hô Mình - Bạn."},
                    history=[{"role": "user" if m["role"]=="user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages[:-1]]
                )
                response = chat.send_message(prompt)
                ai_reply = response.text
                
                with st.chat_message("assistant"):
                    st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                save_user_history(user, st.session_state.messages)
            except Exception as e:
                st.error(f"Hư không lỗi: {e}")
else:
    st.info("🌙 Hãy nhìn sang bên trái, Đăng ký hoặc Đăng nhập để bắt đầu.")
