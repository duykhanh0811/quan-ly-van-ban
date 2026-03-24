import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CẤU HÌNH ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"

# Hàm đọc dữ liệu không cần quyền (vì bạn đã công khai Sheets)
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Nội bộ", layout="wide")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Vào hệ thống"):
        df_u = load_data("users")
        if not df_u.empty:
            user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = u
                st.session_state.user_name = user.iloc[0]['fullname']
                st.rerun()
            else: st.error("Sai tài khoản!")

# --- GIAO DIỆN CHÍNH ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư ĐẾN", "📤 GỬI VĂN BẢN"])

    if menu == "📥 Hộp thư ĐẾN":
        st.header("📥 Văn bản gửi cho bạn")
        df_in = load_data("docs_in")
        if not df_in.empty:
            # Lọc đúng văn bản gửi cho receiver là user_id của bạn
            df_mine = df_in[df_in['receiver'].astype(str) == st.session_state.user_id]
            st.dataframe(df_mine, use_container_width=True)
        else: st.info("Hộp thư trống.")

    elif menu == "📤 GỬI VĂN BẢN":
        st.header("📤 Soạn văn bản mới")
        # Lấy danh sách user để chọn người nhận
        df_all = load_data("users")
        list_users = df_all['username'].tolist() if not df_all.empty else []
        
        with st.form("form_gui"):
            target = st.selectbox("Người nhận", list_users)
            sh = st.text_input("Số hiệu")
            nd = st.text_area("Nội dung")
            
            # Nút bấm quan trọng để tránh lỗi "Missing Submit Button"
            if st.form_submit_button("🚀 GỬI NGAY"):
                # Ghi chú: Vì không dùng API, bạn hãy dán thủ công dòng này vào Sheets 
                # Hoặc dùng Google Form để tự động hóa phần Ghi (Write)
                st.success(f"Đã tạo lệnh gửi cho {target}!")
                st.code(f"{sh}, {datetime.now().strftime('%d/%m/%Y')}, {st.session_state.user_name}, {nd}, {st.session_state.user_id}, {target}")
                st.info("Copy dòng trên dán vào sheet 'docs_in' là xong!")