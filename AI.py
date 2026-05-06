import streamlit as st
import requests
import os
import json

# --- 1. GIAO DIỆN ---
st.set_page_config(page_title="AI Soulmate", page_icon="🌙", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    p, span, label, li, h1, h2, h3, .stMarkdown { color: #FFFFFF !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stToolbar"] { display: none !important; }
    footer, header { visibility: hidden; }
    .stTextInput input { background-color: #1a1a1a !important; color: white !important; border-radius: 10px !important; }
    .stButton>button { width: 100%; background-color: #ffffff !important; color: #000000 !important; border-radius: 20px !important; }
    .stChatMessage { background-color: #111111 !important; border: 1px solid #222 !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LƯU TRỮ ---
USER_DB = "users_db.json"
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return default
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. LOGIC ĐĂNG NHẬP ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><h1 style='text-align: center;'>🌙 AI Soulmate</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_l, tab_r = st.tabs(["Đăng nhập", "Đăng ký"])
        with tab_l:
            u = st.text_input("Tên", key="l_u")
            p = st.text_input("Mật mã", type="password", key="l_p")
            if st.button("Vào thôi"):
                users = load_json(USER_DB, {})
                if u in users and users[u] == p:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.session_state.messages = load_json(f"history_{u}.json", [])
                    st.rerun()
                else: st.error("Sai rồi kìa!")
        with tab_r:
            nu = st.text_input("Tên mới", key="r_u")
            np = st.text_input("Mật mã mới", type="password", key="r_p")
            if st.button("Đăng ký"):
                if nu and np:
                    db = load_json(USER_DB, {})
                    db[nu] = np
                    save_json(USER_DB, db)
                    st.success("Xong! Qua đăng nhập nhé.")
else:
    user = st.session_state.current_user
    if "messages" not in st.session_state:
        st.session_state.messages = load_json(f"history_{user}.json", [])

    c1, c2 = st.columns([5, 1])
    with c1: st.title(f"🌙 Tri kỷ của {user}")
    with c2: 
        if st.button("Thoát"):
            st.session_state.logged_in = False
            st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Nói gì đi..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        API_KEY = st.secrets.get("APIKEY") or os.getenv("APIKEY")
        
        if API_KEY:
            try:
                # ÉP DÙNG ENDPOINT /v1 (THAY VÌ v1beta) ĐỂ FIX LỖI 404
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={API_KEY}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                
                response = requests.post(url, headers=headers, json=data)
                res_json = response.json()
                
                if response.status_code == 200:
                    bot_msg = res_json['candidates'][0]['content']['parts'][0]['text']
                else:
                    bot_msg = f"Lỗi từ Google ({response.status_code}): {res_json.get('error', {}).get('message', 'Không rõ lỗi')}"
                
            except Exception as e:
                bot_msg = f"Lỗi hệ thống: {str(e)}"
        else: 
            bot_msg = "Cậu chưa thiết lập API Key trong Secrets!"

        st.session_state.messages.append({"role": "assistant", "content": bot_msg})
        with st.chat_message("assistant"): st.markdown(bot_msg)
        save_json(f"history_{user}.json", st.session_state.messages)
