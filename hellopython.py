import streamlit as st
import pandas as pd
from datetime import datetime

# --- KẾT NỐI GOOGLE SHEETS (DÙNG LINK CSV) ---
# DÁN LINK GOOGLE SHEETS CỦA BẠN VÀO ĐÂY (Thay thế link ví dụ bên dưới)
# Lưu ý: Link này phải ở chế độ "Anyone with the link can edit"
SHEET_ID = "ID_FILE_CUA_BAN" # Đoạn mã nằm giữa /d/ và /edit trong link của bạn
LINK_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=users"
LINK_IN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_in"
LINK_OUT = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_out"

# Hàm đọc dữ liệu
def load_data(link):
    try:
        return pd.read_csv(link)
    except:
        return pd.DataFrame()

# --- GIAO DIỆN ---
st.set_page_config(page_title="Hệ thống Văn bản Online", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🔐 Đăng nhập hệ thống chung")
    u = st.text_input("Tên đăng nhập")
    p = st.text_input("Mật khẩu", type="password")
    
    col1, col2 = st.columns(2)
    if col1.button("Đăng nhập"):
        df_users = load_data(LINK_USERS)
        # Kiểm tra tài khoản trong Google Sheets
        user = df_users[(df_users['username'] == u) & (df_users['password'].astype(str) == p)]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.user_name = user.iloc[0]['fullname']
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu! Hãy kiểm tra lại file Google Sheets.")
    
    st.info("💡 Mẹo: Bạn hãy nhập tài khoản trực tiếp vào file Google Sheets ở Sheet 'users' trước nhé!")

# --- MÀN HÌNH CHÍNH (SAU KHI LOGIN) ---
else:
    st.sidebar.success(f"Chào mừng: {st.session_state.user_name}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("CHỨC NĂNG", ["Văn bản ĐẾN", "Văn bản ĐI"])

    if menu == "Văn bản ĐẾN":
        st.header("📥 Danh sách Văn bản Đến (Dữ liệu chung)")
        # Hiển thị dữ liệu từ Google Sheets
        df_in = load_data(LINK_IN)
        st.dataframe(df_in, use_container_width=True)
        
        with st.expander("Thêm văn bản mới"):
            with st.form("form_in"):
                so = st.text_input("Số hiệu")
                gui = st.text_input("Nơi gửi")
                nd = st.text_area("Trích yếu")
                if st.form_submit_button("Gửi lên hệ thống"):
                    st.warning("Tính năng ghi trực tiếp từ Web vào Sheets cần cấu hình API. Hiện tại bạn có thể nhập trực tiếp vào file Sheets để mọi người cùng thấy!")

    elif menu == "Văn bản ĐI":
        st.header("📤 Danh sách Văn bản Đi (Dữ liệu chung)")
        df_out = load_data(LINK_OUT)
        st.dataframe(df_out, use_container