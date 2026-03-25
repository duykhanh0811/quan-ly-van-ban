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
        df = pd.read_csv(url)
        return df.fillna("") # Xử lý các ô trống để tránh lỗi
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Học đường", layout="wide")

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký"])
    with tab1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Xác nhận"):
            df_u = load_data("users")
            if not df_u.empty:
                user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_id = u
                    st.session_state.user_name = user.iloc[0]['fullname']
                    # Fix lỗi AttributeError bằng cách gán giá trị mặc định nếu trống
                    st.session_state.user_role = user.iloc[0].get('role', 'Chưa xác định')
                    st.session_state.id_code = user.iloc[0].get('id_code', 'N/A')
                    st.rerun()
                else: st.error("Sai tài khoản!")

    with tab2:
        st.subheader("Tạo tài khoản mới")
        r_u = st.text_input("Username", key="reg_u")
        r_f = st.text_input("Họ và Tên", key="reg_f")
        r_id = st.text_input("Mã định danh (MSSV/MSGV)", key="reg_id")
        r_role = st.selectbox("Chức vụ", ["Sinh viên", "Giảng viên", "Nhà trường"])
        r_p = st.text_input("Mật khẩu", type="password", key="reg_p")
        
        if st.button("Đăng ký ngay"):
            payload = {"type": "register", "username": r_u, "password": r_p, "fullname": r_f, "id_code": r_id, "role": r_role}
            requests.post(WEB_APP_URL, json=payload)
            st.success("✅ Đã đăng ký thành công!")

# --- GIAO DIỆN CHÍNH ---
else:
    # Sidebar hiển thị thông tin an toàn
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.write(f"🏷️ **Chức vụ:** {st.session_state.user_role}")
    st.sidebar.write(f"🆔 **ID:** {st.session_state.id_code}")
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư", "📤 Gửi văn bản"])

    if menu == "📥 Hộp thư":
        st.header("📥 Văn bản gửi cho bạn")
        df_in = load_data("docs_in")
        if not df_in.empty:
            df_mine = df_in[df_in['receiver'].astype(str) == st.session_state.user_id]
            st.dataframe(df_mine, use_container_width=True)

    elif menu == "📤 Gửi văn bản":
        st.header("📤 Soạn văn bản")
        df_u = load_data("users")
        list_users = df_u['username'].tolist() if not df_u.empty else []
        
        with st.form("send_form"):
            target = st.selectbox("Người nhận", list_users)
            sh = st.text_input("Số hiệu")
            nd = st.text_area("Nội dung")
            if st.form_submit_button("🚀 GỬI TỰ ĐỘNG"):
                payload = {
                    "type": "send", "so_hieu": sh, "ngay": datetime.now().strftime("%d/%m/%Y"),
                    "gui": f"{st.session_state.user_name} ({st.session_state.user_role})",
                    "noi_dung": nd, "sender": st.session_state.user_id, "receiver": target,
                    "role_sender": st.session_state.user_role
                }
                requests.post(WEB_APP_URL, json=payload)
                st.success("✅ Đã gửi thành công!")