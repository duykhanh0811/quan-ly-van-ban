import streamlit as st
import pandas as pd
from datetime import datetime

# --- KẾT NỐI DỮ LIỆU (Giữ nguyên link của bạn) ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
LINK_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=users"
LINK_IN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_in"
LINK_OUT = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_out"

# Khởi tạo bộ nhớ tạm để lưu dữ liệu mới nhập trên web
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
            user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = user.iloc[0]['fullname']
                st.rerun()
            else: st.error("Sai tài khoản!")

    with tab_reg:
        st.subheader("Tạo tài khoản mới")
        new_u = st.text_input("Chọn tên đăng nhập")
        new_p = st.text_input("Chọn mật khẩu", type="password")
        new_f = st.text_input("Họ và tên đầy đủ")
        if st.button("Hoàn tất đăng ký"):
            st.success(f"Đã ghi nhận yêu cầu cho {new_f}! (Lưu ý: Bạn hãy báo admin thêm dòng này vào Google Sheets để kích hoạt nhé)")

# --- GIAO DIỆN QUẢN LÝ ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["🏠 Trang chủ", "📥 Văn bản ĐẾN", "📤 Văn bản ĐI"])
    if st.sidebar.button("Thoát"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "📥 Văn bản ĐẾN":
        st.header("📥 Quản lý Văn bản Đến")
        # Form nhập liệu
        with st.expander("➕ THÊM VĂN BẢN MỚI", expanded=True):
            with st.form("in_form"):
                col1, col2 = st.columns(2)
                sh = col1.text_input("Số hiệu")
                ng = col2.date_input("Ngày nhận")
                nguoi = col1.text_input("Nơi gửi")
                nd = st.text_area("Trích yếu nội dung")
                if st.form_submit_button("Lưu văn bản"):
                    new_row = pd.DataFrame([{'so_hieu':sh, 'ngay_den':ng, 'noi_gui':nguoi, 'noi_dung':nd}])
                    st.session_state.temp_in = pd.concat([st.session_state.temp_in, new_row], ignore_index=True)
                    st.toast("Đã thêm vào danh sách hiển thị!")

        # Hiển thị dữ liệu (Gộp từ Sheets + Dữ liệu vừa nhập)
        st.subheader("📂 Danh sách hiện tại")
        df_in = pd.concat([load_data(LINK_IN), st.session_state.temp_in], ignore_index=True)
        st.dataframe(df_in, use_container_width=True)

    elif menu == "📤 Văn bản ĐI":
        st.header("📤 Quản lý Văn bản Đi")
        with st.expander("➕ SOẠN VĂN BẢN ĐI", expanded=True):
            with st.form("out_form"):
                col1, col2 = st.columns(2)
                sd = col1.text_input("Số ký hiệu")
                nd_di = col2.date_input("Ngày ban hành")
                nhan = col1.text_input("Nơi nhận")
                ky = col2.text_input("Người ký")
                ndung = st.text_area("Nội dung tóm tắt")