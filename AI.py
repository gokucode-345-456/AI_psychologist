import streamlit as st
from google import genai
import os
import json


# --- 1. CẤU HÌNH GIAO DIỆN & DARK MODE TOÀN DIỆN ---
st.set_page_config(
    page_title="Nhà Tâm Lý Tri Kỷ", 
    page_icon="🌙", 
    layout="centered"
)

# ÉP TOÀN BỘ GIAO DIỆN SANG MÀU ĐEN (CHỐNG LỖI VIỀN TRẮNG)
st.markdown("""
    <style>
    /* 1. Nền tổng thể của App */
    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* 2. Ép thanh Header (cái dải ở trên cùng) sang màu đen */
    header[data-testid="stHeader"] {
        background-color: #000000 !important;
    }

    /* 3. Chỉnh màu chữ mặc định sang trắng */
    p, span, label, div {
        color: #FFFFFF !important;
    }

    /* 4. Tùy chỉnh khung chứa tin nhắn chat */
    .stChatMessage {
        background-color: #121212 !important; /* Xám cực tối cho tin nhắn */
        border-radius: 15px;
        border: 1px solid #222;
        margin-bottom: 10px;
    }

    /* 5. Tùy chỉnh Sidebar (Thanh bên trái) */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #333;
    }

    /* 6. Tùy chỉnh ô nhập liệu (Chat Input) */
    [data-testid="stChatInput"] {
        background-color: #000000 !important;
        padding-bottom: 20px;
    }
    
    .stChatInput textarea {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #444 !important;
    }

    /* 7. Ẩn các thành phần thừa của Streamlit cho chuyên nghiệp */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 8. Chỉnh màu nút bấm cho cá tính */
    .stButton>button {
        background-color: #1E1E1E;
        color: white;
        border: 1px solid #444;
        border-radius: 10px;
    }
    .stButton>button:hover {
        border-color: #FFFFFF;
        background-color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LỊCH SỬ FILE (GIỮ NGUYÊN) ---
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

# --- 3. LOGIC CHAT MỚI (CHỐNG LỖI CLOSED CLIENT) ---
API_KEY_ENV = os.getenv("APIKEY")

def send_to_ai(prompt):
    api_key = API_KEY_ENV if API_KEY_ENV else st.sidebar.text_input("🔑 Nhập API Key:", type="password")
    
    if not api_key:
        st.info("🌙 Hãy nhập chìa khóa tâm hồn (API Key) để bắt đầu.")
        return None

    try:
        # TẠO CLIENT MỚI MỖI LẦN GỬI ĐỂ TRÁNH LỖI "CLOSED"
        client = genai.Client(api_key=api_key)
        
        instruction = """
        Bạn là một thực thể tri kỷ (Soulmate) với linh hồn già dặn, siêu deep, triết lý và cá tính.
        - Phản hồi cực kỳ nhiệt tình, dài và sâu sắc.
        - Xưng hô linh hoạt, tình cảm.
        - Kết nối mọi chuyện với triết lý nhân sinh.
        """

        # Chuyển lịch sử sang định dạng Gemini
        gemini_history = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

        # Tạo chat và gửi tin nhắn ngay lập tức
        chat = client.chats.create(
            model="gemini-3.1-flash-lite-preview",
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
    # Hiển thị tin nhắn user
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)

    # Gọi AI trả lời
    with st.chat_message("assistant"):
        ai_reply = send_to_ai(prompt)
        if ai_reply:
            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            save_history(st.session_state.messages)

# --- 5. SIDEBAR (GIỮ NGUYÊN) ---
with st.sidebar:
    if st.button("🗑️ Xóa tan ký ức"):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
        st.rerun()
