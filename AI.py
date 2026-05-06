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

# CSS "CỨU CÁNH": TẠO NÚT MỞ SIDEBAR KHÔNG THỂ BIẾN MẤT
st.markdown("""
    <style>
    /* Nền đen toàn app */
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }

    /* Sidebar màu đen */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #222;
    }

    /* TẠO NÚT FLOATING ĐỂ MỞ SIDEBAR KHI BỊ ĐÓNG */
    /* Nút này sẽ đè lên vị trí mặc định của Streamlit */
    [data-testid="collapsedControl"] {
        background-color: #FFFFFF !important;
        border-radius: 0 10px 10px 0 !important;
        width: 40px !important;
        height: 40px !important;
        top: 10px !important;
        left: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 2px 2px 10px rgba(255,255,255,0.2) !important;
    }
    
    /* Làm icon mũi tên màu đen cho dễ nhìn trên nền nút trắng */
    [data-testid="collapsedControl"] svg {
        fill: #000000 !important;
        width: 25px !important;
        height: 25px !important;
    }

    /* Nút bấm trong sidebar */
    div.stSidebar div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
        border: none;
    }
    
    /* Ô Chat */
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    
    /* Ẩn toolbar thừa */
    [data-testid="stToolbar"], footer, header { visibility: hidden; }
    </style>
    
    <script>
        // Đoạn script nhỏ để nhắc người dùng nếu họ lỡ đóng sidebar
        var mainContent = window.parent.document.querySelector('.main');
        mainContent.addEventListener('click', function() {
            console.log('Nếu không thấy form, nhấn nút trắng ở góc trái nhé!');
        });
    </script>
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
        st.write("---")
        st.info("Hãy đăng nhập để mở khóa tâm hồn.")
        tab_login, tab_signup = st.tabs(["Đăng nhập", "Đăng ký"])
        
        with tab_signup:
            new_user = st.text_input("Tên định danh:", key="reg_user")
            new_pass = st.text_input("Mật mã:", type="password", key="reg_pass")
            if st.button("Xác nhận đăng ký"):
                if new_user and new_pass:
                    save_user(new_user, new_pass)
                    st.success("Đã đăng ký! Qua tab Đăng nhập thôi.")
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
                else: st.error("Sai mật mã rồi bạn ơi.")
    else:
        st.write(f"👤 Chào mừng, **{st.session_state.current_user}**")
        st.write("---")
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

    # Hiển thị lịch sử chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Xử lý chat
    if prompt := st.chat_input("Nói với mình điều gì đó..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        API_KEY = os.getenv("APIKEY")
        if API_KEY:
            try:
                client = genai.Client(api_key=API_KEY)
                chat = client.chats.create(
                    model="gemini-2.0-flash", # Cập nhật model ổn định hơn
                    config={"system_instruction": "bạn là một học sinh cấp 3 năng động và đầy cá tính, bạn có khả năng đồng cảm người khác, có thể deeptalk nếu người dùng hạ giọng xuống, bạn là 1 người rất an ủi và quan tâm người khác, nhắn tin giống như gen z (dùng icon, viết thường, từ lóng nhẹ), nhắn tin tùy vào trạng thái của người dùng mà dài hoặc ngắn."},
                    history=[{"role": "user" if m["role"]=="user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages[:-1]]
                )
                res = chat.send_message(prompt)
                with st.chat_message("assistant"): st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                save_user_history(user, st.session_state.messages)
            except Exception as e: st.error(f"Lỗi AI: {e}")
        else:
            st.warning("⚠️ Mình chưa thấy API Key. Hãy setup biến môi trường APIKEY nhé!")
else:
    # Giao diện chào mừng khi chưa đăng nhập
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h1>🌙 Chào cậu, tớ là AI Soulmate</h1>
        <p>Tớ ở đây để lắng nghe và chia sẻ cùng cậu mọi lúc.</p>
        <div style="background: #111; padding: 20px; border-radius: 15px; border: 1px dashed #444;">
            <p>Nhìn sang <b>góc trái phía trên</b>, có một nút màu trắng.</p>
            <p>Nhấn vào đó để <b>Đăng nhập</b> và bắt đầu nhé!</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
