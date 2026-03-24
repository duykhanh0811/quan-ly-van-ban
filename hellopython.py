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
                # Kiểm tra tài khoản (ép kiểu về string để so sánh