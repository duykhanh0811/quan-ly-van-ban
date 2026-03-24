import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CẤU HÌNH ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
# Link Apps Script bạn vừa tạo
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwKjL7c8sDm-mJwKlUuOS1K4f5n6EW_AdaUzBI0WLFSE6pJbEwRnhGhugrs0qaIo6fDFg/exec"

def load_data(sheet_name):
    # Đọc dữ liệu công khai từ Sheets
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Văn bản Tự động", layout="wide")

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Xác nhận"):
        df_u = load_data("users")
        if not df_u.empty:
            # So khớp tài khoản từ sheet 'users'
            user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = u
                st.session_state.user_name = user.iloc[0]['fullname']
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu!")

# --- GIAO DIỆN SAU KHI ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư ĐẾN", "📤 GỬI VĂN BẢN"])

    if menu == "📥 Hộp thư ĐẾN":
        st.header("📥 Văn bản gửi cho bạn")
        df_in = load_data("docs_in")
        if not df_in.empty:
            # Lọc đúng văn bản có receiver là tên đăng nhập của mình
            df_mine = df_in[df_in['receiver'].astype(str) == st.session_state.user_id]
            st.dataframe(df_mine, use_container_width=True)
        else: 
            st.info("Hộp thư trống.")

    elif menu == "📤 GỬI VĂN BẢN":
        st.header("📤 Soạn văn bản gửi đi")
        df_all = load_data("users")
        list_users = df_all['username'].tolist() if not df_all.empty else []
        
        with st.form("form_gui_tu_dong"):
            target = st.selectbox("Người nhận", list_users)
            sh = st.text_input("Số hiệu văn bản")
            nd = st.text_area("Nội dung trích yếu")
            
            # Nút bấm nằm trong form để tránh lỗi Submit Button
            submit = st.form_submit_button("🚀 GỬI VÀ LƯU TỰ ĐỘNG")
            
            if submit:
                # Chuẩn bị dữ liệu gửi lên Apps Script
                payload = {
                    "so_hieu": sh,
                    "ngay": datetime.now().strftime("%d/%m/%Y"),
                    "gui": st.session_state.user_name,
                    "noi_dung": nd,
                    "sender": st.session_state.user_id,
                    "receiver": target
                }
                
                try:
                    # Gửi yêu cầu POST tự động ghi vào Sheets
                    response = requests.post(WEB_APP_URL, json=payload)
                    if response.status_code == 200:
                        st.success(f"✅ Tuyệt vời! Đã gửi thành công cho {target}.")
                        st.balloons() # Hiệu ứng chúc mừng
                    else:
                        st.error("Lỗi: Không thể ghi vào Sheets. Hãy kiểm tra lại link /exec.")
                except:
                    st.error("Lỗi kết nối!")