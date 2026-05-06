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

# CSS: Giữ vibe đen tuyền, nút trắng, khóa sidebar
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #222; }
    
    /* Nút trắng cho sidebar */
    div.stSidebar div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }
    
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    .stChatInput textarea { background-color: #1A1A1A !important; color: #FFFFFF !important; }
    [data-testid="stToolbar"], footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HỆ THỐNG LƯU TRỮ THEO USER ---
def get_history_file(username):
    return f"history_{username}.json"

def save_user_history(username, messages):
    with open(get_history_file(username), "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_user_history(username):
    file_path = get_history_file(username)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- 3. ĐĂNG NHẬP (SIDEBAR) ---
with st.sidebar:
    st.title("🔐 Đăng nhập")
    user_input = st.text_input("Tên định danh:", placeholder="Ví dụ: tung_nui")
    pass_input = st.text_input("Mật mã tâm hồn:", type="password")
    
    # Một số tài khoản mẫu (Ông có thể tự thêm ở đây)
    USERS = {"admin": "123", "user1": "6789", "tung": "deptrai"}

    logged_in = False
    if user_input and pass_input:
        if user_input in USERS and USERS[user_input] == pass_input:
            logged_in = True
            st.success(f"Chào mừng {user_input} quay lại!")
        else:
            st.error("Mật mã hoặc tên không đúng.")

    st.divider()
    
    if logged_in:
        if st.button("➕ Cuộc trò chuyện mới"):
            st.session_state.messages = []
            save_user_history(user_input, [])
            st.rerun()

# --- 4. XỬ LÝ CHAT ---
if logged_in:
    # Load lịch sử riêng của User đó
    if "current_user" not in st.session_state or st.session_state.current_user != user_input:
        st.session_state.current_user = user_input
        st.session_state.messages = load_user_history(user_input)

    st.title(f"🌙 Tri kỷ của {user_input}")

    # Hiển thị chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Nhập chat
    if prompt := st.chat_input("Nói gì đi..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gọi AI (Dùng API Key từ Env hoặc Code)
        API_KEY = os.getenv("APIKEY") 
        if not API_KEY:
            st.warning("Thiếu API Key trong Environment!")
        else:
            try:
                client = genai.Client(api_key=API_KEY)
                chat = client.chats.create(
                    model="gemini-3.1-flash-lite-preview",
                    config={"system_instruction": "nhắn deep tí , nhưng cũng hòa đồng, vui vẻ , nếu giọng điệu người dùng có tí deep thì bạn cũng phải deep theo"},
                    history=[{"role": "user" if m["role"]=="user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages[:-1]]
                )
                response = chat.send_message(prompt)
                ai_reply = response.text
                
                with st.chat_message("assistant"):
                    st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                
                # Lưu vào file riêng của User
                save_user_history(user_input, st.session_state.messages)
            except Exception as e:
                st.error(f"Lỗi AI: {e}")
else:
    st.info("🌙 đăng nhập mới đc dùng")
    st.stop()
