import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CẤU HÌNH ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwKjL7c8sDm-mJwKlUuOS1K4f5n6EW_AdaUzBI0WLFSE6pJbEwRnhGhugrs0qaIo6fDFg/exec"

def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Quản lý Học đường", layout="wide")

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký thành viên"])
    
    with tab1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Đăng nhập"):
            df_u = load_data("users")
            if not df_u.empty:
                user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_id = u
                    st.session_state.user_name = user.iloc[0]['fullname']
                    st.session_state.user_role = user.iloc[0]['role']
                    st.session_state.id_code = user.iloc[0]['id_code']
                    st.rerun()
                else: st.error("Sai thông tin đăng nhập!")

    with tab2:
        new_u = st.text_input("Tên đăng nhập", key="r_u")
        new_f = st.text_input("Họ và Tên", key="r_f")
        new_id = st.text_input("Mã định danh (MSSV/MSGV)", key="r_id")
        # Thêm phần chọn chức vụ
        new_role = st.selectbox("Chức vụ", ["Sinh viên", "Giảng viên", "Nhà trường"])
        new_p = st.text_input("Mật khẩu", type="password", key="r_p")
        
        if st.button("Tạo tài khoản"):
            if new_u and new_f and new_id:
                payload = {
                    "type": "register",
                    "username": new_u,
                    "password": new_p,
                    "fullname": new_f,
                    "id_code": new_id,
                    "role": new_role
                }
                requests.post(WEB_APP_URL, json=payload)
                st.success("Đăng ký thành công!")
            else: st.warning("Vui lòng nhập đủ thông tin.")

# --- GIAO DIỆN CHÍNH ---
else:
    st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
    st.sidebar.info(f"Chức vụ: {st.session_state.user_role}\n\nID: {st.session_state.id_code}")
    
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư", "📤 Gửi văn bản"])

    if menu == "📥 Hộp thư":
        st.header(f"📥 Văn bản dành cho {st.session_state.user_role}")
        df_in = load_data("docs_in")
        if not df_in.empty:
            df_mine = df_in[df_in['receiver'].astype(str) == st.session_state.user_id]
            st.dataframe(df_mine, use_container_width=True)

    elif menu == "📤 Gửi văn bản":
        st.header("📤 Soạn văn bản mới")
        df_all = load_data("users")
        list_users = df_all['username'].tolist() if not df_all.empty else []
        
        with st.form("send_form"):
            target = st.selectbox("Gửi đến", list_users)
            sh = st.text_input("Số hiệu")
            nd = st.text_area("Nội dung")
            if st.form_submit_button("Gửi ngay"):
                payload = {
                    "type": "send",
                    "so_hieu": sh,
                    "ngay": datetime.now().strftime("%d/%m/%Y"),
                    "gui": f"{st.session_state.user_name} ({st.session_state.user_role})",
                    "noi_dung": nd,
                    "sender": st.session_state.user_id,
                    "receiver": target,
                    "role_sender": st.session_state.user_role
                }
                requests.post(WEB_APP_URL, json=payload)
                st.success("Đã gửi văn bản thành công!")