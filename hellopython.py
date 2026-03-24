import streamlit as st
import pandas as pd
from datetime import datetime

# --- KẾT NỐI DỮ LIỆU ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
LINK_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=users"
LINK_IN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_in"
LINK_OUT = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_out"

# Khởi tạo bộ nhớ tạm
if 'temp_in' not in st.session_state: st.session_state.temp_in = pd.DataFrame()
if 'temp_out' not in st.session_state: st.session_state.temp_out = pd.DataFrame()

def load_data(link):
    try: return pd.read_csv(link)
    except: return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Văn bản Toàn diện", layout="wide")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- GIAO DIỆN ĐĂNG NHẬP & ĐĂNG KÝ ---
if not st.session_state.logged_in:
    tab_login, tab_reg = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký tài khoản mới"])
    
    with tab_login:
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("Vào hệ thống"):
            df_u = load_data(LINK_USERS)
            if not df_u.empty:
                user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user.iloc[0]['fullname']
                    st.rerun()
                else: st.error("Sai tài khoản hoặc mật khẩu!")

    with tab_reg:
        st.subheader("Đăng ký tài khoản")
        with st.form("reg_form"):
            new_u = st.text_input("Tên đăng nhập mới")
            new_p = st.text_input("Mật khẩu mới", type="password")
            new_f = st.text_input("Họ và tên đầy đủ")
            reg_btn = st.form_submit_button("Gửi yêu cầu đăng ký")
            if reg_btn:
                st.info(f"Yêu cầu cho '{new_f}' đã được tạo. Vui lòng báo Admin thêm vào Google Sheets!")

# --- GIAO DIỆN QUẢN LÝ ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["🏠 Trang chủ", "📥 Văn bản ĐẾN", "📤 Văn bản ĐI"])
    if st.sidebar.button("Thoát"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "🏠 Trang chủ":
        st.header("Chào mừng bạn đến với hệ thống quản lý văn bản")
        st.write("Dữ liệu được đồng bộ trực tiếp với Google Sheets của bạn.")

    elif menu == "📥 Văn bản ĐẾN":
        st.header("📥 Quản lý Văn bản Đến")
        with st.expander("➕ THÊM VĂN BẢN ĐẾN", expanded=True):
            with st.form("in_form"):
                sh = st.text_input("Số hiệu")
                ng = st.date_input("Ngày nhận", datetime.now())
                nguoi = st.text_input("Nơi gửi")
                nd = st.text_area("Trích yếu nội dung")
                # Nút Submit phải nằm trong khối 'with st.form'
                submit_in = st.form_submit_button("Lưu văn bản")
                if submit_in:
                    new_row = pd.DataFrame([{'so_hieu':sh, 'ngay_den':ng, 'noi_gui':nguoi, 'noi_dung':nd}])
                    st.session_state.temp_in = pd.concat([st.session_state.temp_in, new_row], ignore_index=True)
                    st.success("Đã thêm vào danh sách hiển thị!")

        st.subheader("📂 Danh sách hiện tại")
        df_in = pd.concat([load_data(LINK_IN), st.session_state.temp_in], ignore_index=True)
        st.dataframe(df_in, use_container_width=True)

    elif menu == "📤 Văn bản ĐI":
        st.header("📤 Quản lý Văn bản Đi")
        with st.expander("➕ SOẠN VĂN BẢN ĐI", expanded=True):
            with st.form("out_form"):
                col1, col2 = st.columns(2)
                sd = col1.text_input("Số ký hiệu")
                nd_di = col2.date_input("Ngày ban hành", datetime.now())
                nhan = col1.text_input("Nơi nhận")
                ky = col2.text_input("Người ký")
                ndung = st.text_area("Nội dung tóm tắt")
                # Sửa lỗi: Đặt nút Submit vào đúng form
                submit_out = st.form_submit_button("Phát hành")
                if submit_out:
                    new_out = pd.DataFrame([{'so_di':sd, 'ngay_di':nd_di, 'noi_nhan':nhan, 'nguoi_ky':ky, 'noi_dung':ndung}])
                    st.session_state.temp_out = pd.concat([st.session_state.temp_out, new_out], ignore_index=True)
                    st.success("Đã ghi nhật ký văn bản đi!")

        st.subheader("📂 Nhật ký văn bản đi")
        df_out = pd.concat([load_data(LINK_OUT), st.session_state.temp_out], ignore_index=True)
        st.dataframe(df_out, use_container_width=True)