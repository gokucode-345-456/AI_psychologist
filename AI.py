import streamlit as st
from google import genai
import os
import json

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="AI Soulmate", page_icon="🌙", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
    .stTextInput input { background-color: #1a1a1a !important; color: white !important; border-radius: 10px !important; }
    .stButton>button { width: 100%; background-color: #ffffff !important; color: #000000 !important; border-radius: 20px !important; font-weight: bold !important; }
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    [data-testid="stToolbar"], footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HÀM XỬ LÝ DỮ LIỆU (JSON) ---
USER_DB = "users_db.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB, "w") as f: json.dump(users, f)

def load_history(username):
    path = f"history_{username}.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_history(username, messages):
    path = f"history_{username}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# --- 3. LOGIC ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🌙 AI Soulmate</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])
            with tab1:
                u = st.text_input("Tên của cậu", key="login_u")
                p = st.text_input("Mật mã", type="password", key="login_p")
                if st.button("Vào thế giới tri kỷ"):
                    users = load_users()
                    if u in users and users[u] == p:
                        st.session_state.logged_in = True
                        st.session_state.current_user = u
                        # QUAN TRỌNG: Load lịch sử ngay khi đăng nhập
                        st.session_state.messages = load_history(u)
                        st.rerun()
                    else: st.error("Sai thông tin rồi nè.")
            with tab2:
                nu = st.text_input("Tên định danh mới", key="reg_u")
                np = st.text_input("Mật mã mới", type="password", key="reg_p")
                if st.button("Tạo tài khoản"):
                    if nu and np:
                        save_user(nu, np)
                        st.success("Xong rồi! Qua đăng nhập thôi.")

# --- 4. GIAO DIỆN CHAT ---
else:
    user = st.session_state.current_user
    
    # Đảm bảo messages luôn tồn tại trong session
    if "messages" not in st.session_state:
        st.session_state.messages = load_history(user)

    # Header
    col_t1, col_t2 = st.columns([5, 1])
    with col_t1: st.title(f"🌙 Tri kỷ của {user}")
    with col_t2: 
        if st.button("Thoát"):
            save_history(user, st.session_state.messages) # Lưu trước khi thoát
            st.session_state.logged_in = False
            del st.session_state.messages
            st.rerun()

    # Hiển thị hội thoại
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Xử lý chat
    if prompt := st.chat_input("Nói gì đó với tớ đi..."):
        # Thêm tin nhắn user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gọi AI (Nhớ thay API_KEY của cậu vào)
        API_KEY = os.getenv("APIKEY") 
        if API_KEY:
            try:
                client = genai.Client(api_key=API_KEY)
                # Gửi toàn bộ lịch sử để AI có trí nhớ
                res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt, # Hoặc gửi toàn bộ list tin nhắn tùy vào bản SDK cậu dùng
                    config={"system_instruction": "Bạn là gen Z, nhắn tin ngắn gọn, đồng cảm."}
                )
                response_text = res.text
            except Exception as e:
                response_text = f"Lỗi AI rồi: {e}"
        else:
            response_text = "Tớ đang lắng nghe đây... (Cậu nhớ setup API Key nhé!)"

        # Thêm tin nhắn AI và lưu lại
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
        
        # LƯU NGAY LẬP TỨC VÀO FILE
        save_history(user, st.session_state.messages)
