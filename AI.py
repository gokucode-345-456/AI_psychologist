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

# CSS "TỐI THƯỢNG": BIẾN NÚT MỞ SIDEBAR THÀNH NÚT ĐIỀU KHIỂN CHÍNH
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }

    /* LÀM NỔI BẬT NÚT MỞ SIDEBAR */
    [data-testid="collapsedControl"] {
        background-color: #FFFFFF !important; /* Nút màu trắng */
        border-radius: 50% !important;
        width: 60px !important; /* To hơn */
        height: 60px !important;
        top: 20px !important;
        left: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 20px rgba(255,255,255,0.5) !important;
        animation: pulse 2s infinite; /* Hiệu ứng rung rinh thu hút chú ý */
    }

    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 15px rgba(255, 255, 255, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
    }
    
    [data-testid="collapsedControl"] svg {
        fill: #000000 !important;
        width: 30px !important;
        height: 30px !important;
    }

    /* Sidebar & Button */
    section[data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #222; }
    div.stSidebar div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 12px;
        font-weight: bold;
        border: none;
    }
    
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

# --- 3. SIDEBAR ---
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
            if st.button("Vào thế giới tri kỷ"):
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
        if st.button("🚪 Tạm biệt"):
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
        
        # Gọi AI ở đây (Giữ nguyên logic API Key của bạn)
        API_KEY = os.getenv("APIKEY")
        if API_KEY:
            try:
                client = genai.Client(api_key=API_KEY)
                res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config={"system_instruction": "bạn là một học sinh cấp 3 năng động gen Z, biết lắng nghe, hay dùng icon, nhắn tin ngắn gọn hoặc sâu sắc tùy vibe."}
                )
                with st.chat_message("assistant"): st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                save_user_history(user, st.session_state.messages)
            except Exception as e: st.error(f"Lỗi AI: {e}")
else:
    # Màn hình chờ (Như trong ảnh của bạn nhưng thêm hướng dẫn)
    st.markdown("""
    <div style="text-align: center; margin-top: 100px;">
        <h1 style="font-size: 3rem;">🌙 Chào cậu, tớ là AI Soulmate</h1>
        <p style="font-size: 1.2rem; opacity: 0.8;">Tớ ở đây để lắng nghe và chia sẻ cùng cậu mọi lúc.</p>
        <div style="margin-top: 50px; padding: 20px; border: 1px solid #333; border-radius: 20px; background: #0a0a0a;">
            <p>Hãy nhấn vào <b>Vòng tròn trắng đang nhấp nháy</b> ở góc trái phía trên</p>
            <p>để Đăng nhập và bắt đầu cuộc hành trình nhé! ✨</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
