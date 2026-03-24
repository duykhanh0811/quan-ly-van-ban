import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Hệ thống Văn bản Tự động", layout="wide")

# --- KẾT NỐI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl=0) # ttl=0 để luôn lấy dữ liệu mới nhất

# --- ĐĂNG NHẬP ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP TỰ ĐỘNG")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Đăng nhập"):
        df_u = get_data("users")
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
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư ĐẾN", "📤 Gửi văn bản ĐI"])
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "📥 Hộp thư ĐẾN":
        st.header("📥 Văn bản gửi cho bạn")
        df_in = get_data("docs_in")
        if not df_in.empty and 'receiver' in df_in.columns:
            df_mine = df_in[df_in['receiver'].astype(str) == st.session_state.user_id]
            st.dataframe(df_mine, use_container_width=True)
        else: st.info("Hộp thư trống")

    elif menu == "📤 Gửi văn bản ĐI":
        st.header("📤 Soạn và Gửi tự động")
        
        # Lấy danh sách người nhận từ sheet users
        df_u = get_data("users")
        list_users = df_u['username'].tolist()

        with st.form("send_form"):
            target = st.selectbox("Người nhận", list_users)
            so_h = st.text_input("Số hiệu")
            noi_dung = st.text_area("Nội dung")
            
            if st.form_submit_button("🚀 GỬI NGAY (Tự động lưu vào Sheets)"):
                # 1. Lấy dữ liệu cũ
                existing_data = get_data("docs_in")
                # 2. Tạo dòng mới
                new_row = pd.DataFrame([{
                    "so_hieu": so_h,
                    "ngay_den": datetime.now().strftime("%Y-%m-%d"),
                    "noi_gui": st.session_state.user_name,
                    "noi_dung": noi_dung,
                    "sender": st.session_state.user_id,
                    "receiver": target
                }])
                # 3. Ghi đè lại Sheets với dữ liệu đã thêm dòng mới
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="docs_in", data=updated_df)
                
                st.success(f"✅ Đã gửi thành công cho {target} và tự động lưu vào Google Sheets!")