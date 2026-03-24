import streamlit as st
import pandas as pd
from datetime import datetime

# --- KẾT NỐI GOOGLE SHEETS ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
LINK_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=users"
LINK_IN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_in"
LINK_OUT = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_out"

# Hàm tải dữ liệu từ Sheets
def load_data(link):
    try:
        # Thêm header để tránh lỗi cache của Google
        return pd.read_csv(link)
    except Exception as e:
        return pd.DataFrame()

# --- GIAO DIỆN ---
st.set_page_config(page_title="Hệ thống Văn bản Đại học Online", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🏛️ ĐĂNG NHẬP HỆ THỐNG VĂN BẢN")
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("Xác nhận đăng nhập"):
            df_users = load_data(LINK_USERS)
            if not df_users.empty:
                # Kiểm tra tài khoản (ép kiểu về string để so sánh chính xác)
                user = df_users[(df_users['username'].astype(str) == u) & (df_users['password'].astype(str) == p)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user.iloc[0]['fullname']
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")
            else:
                st.error("Không thể kết nối dữ liệu người dùng!")
    
    with col_r:
        st.info("📢 Hướng dẫn: Quản trị viên cần nhập tài khoản vào Sheet 'users' trước khi đăng nhập tại đây.")

# --- MÀN HÌNH CHÍNH ---
else:
    st.sidebar.title("MENU")
    st.sidebar.write(f"👤 Người dùng: **{st.session_state.user_name}**")
    
    menu = st.sidebar.radio("Chọn chức năng", ["🏠 Trang chủ", "📥 Văn bản ĐẾN", "📤 Văn bản ĐI"])
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "🏠 Trang chủ":
        st.header("Chào mừng bạn đến với hệ thống quản lý văn bản chung")
        st.write("Dữ liệu đang được đồng bộ trực tuyến với Google Sheets.")
        
    elif menu == "📥 Văn bản ĐẾN":
        st.header("📥 Danh sách Văn bản Đến")
        df_in = load_data(LINK_IN)
        if not df_in.empty:
            st.dataframe(df_in, use_container_width=True)
        else:
            st.warning("Chưa có dữ liệu văn bản đến.")

    elif menu == "📤 Văn bản ĐI":
        st.header("📤 Danh sách Văn bản Đi")
        df_out = load_data(LINK_OUT)
        if not df_out.empty:
            st.dataframe(df_out, use_container_width=True)
        else:
            st.warning("Chưa có dữ liệu văn bản đi.")