import streamlit as st

st.title("Test Streamlit")
st.write("Nếu bạn thấy dòng này, nghĩa là Streamlit vẫn chạy tốt!")

if "messages" not in st.session_state:
    st.session_state.messages = []

prompt = st.chat_input("Thử gõ gì đó xem...")
if prompt:
    st.write(f"Bạn vừa gõ: {prompt}")
