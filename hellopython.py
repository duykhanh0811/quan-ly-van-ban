import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Hệ thống Văn bản Tự động", layout="wide")

# --- KẾT NỐI TRỰC TIẾP ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(s_name):
    return conn.read(worksheet=s_name, ttl=0) # ttl=0 để luôn lấy dữ liệu mới nhất

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP TỰ ĐỘNG")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Xác nhận"):
        df_u = load_data("users")
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
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư ĐẾN", "📤 Gửi văn bản MỚI"])

    if menu == "📥 Hộp thư ĐẾN":
        st.header("📥 Văn bản gửi cho bạn")
        df_in = load_data("docs_in")
        # Lọc đúng người nhận là mình
        df_mine = df_in[df_in['receiver'].astype(str) == st.session_state.user_id]
        st.dataframe(df_mine, use_container_width=True)

    elif menu == "📤 Gửi văn bản MỚI":
        st.header("📤 Soạn và Gửi tự động")
        df_u = load_data("users")
        list_users = df_u['username'].tolist()

        with st.form("auto_send_form"):
            target = st.selectbox("Người nhận", list_users)
            so_h = st.text_input("Số hiệu")
            noi_dung = st.text_area("Nội dung")
            
            if st.form_submit_button("🚀 GỬI NGAY"):
                # 1. Lấy dữ liệu hiện tại
                curr_df = load_data("docs_in")
                # 2. Tạo dòng mới
                new_data = pd.DataFrame([{
                    "so_hieu": so_h,
                    "ngay_den": datetime.now().strftime("%d/%m/%Y"),
                    "noi_gui": st.session_state.user_name,
                    "noi_dung": noi_dung,
                    "sender": st.session_state.user_id,
                    "receiver": target
                }])
                # 3. TỰ ĐỘNG GHI VÀO SHEETS
                updated_df = pd.concat([curr_df, new_data], ignore_index=True)
                conn.update(worksheet="docs_in", data=updated_df)
                st.success(f"✅ Đã gửi và lưu tự động vào Sheets cho {target}!")