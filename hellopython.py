import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH LINK GOOGLE SHEETS ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"

# Hàm đọc dữ liệu bằng cách ép Google xuất file CSV
def load_sheet_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={sheet_name}"
    try:
        # Thêm tham số thời gian để tránh bị lưu cache cũ
        df = pd.read_csv(url + f"&cache={datetime.now().timestamp()}")
        return df
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Văn bản Đại học", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG")
    u = st.text_input("Tên đăng nhập (username)")
    p = st.text_input("Mật khẩu", type="password")
    
    if st.button("Xác nhận"):
        df_users = load_sheet_data("users")
        if not df_users.empty:
            # Kiểm tra đúng tài khoản/mật khẩu
            user = df_users[(df_users['username'].astype(str) == u) & (df_users['password'].astype(str) == p)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = u
                st.session_state.user_name = user.iloc[0]['fullname']
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu! (Hãy kiểm tra lại Sheet 'users')")
        else:
            st.error("Không thể kết nối dữ liệu. Hãy đảm bảo tên Sheet là 'users'.")

# --- GIAO DIỆN CHÍNH ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư ĐẾN", "📤 Soạn văn bản GỬI ĐI"])
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    # --- 📥 HỘP THƯ ĐẾN (Chỉ hiện văn bản gửi ĐẾN mình) ---
    if menu == "📥 Hộp thư ĐẾN":
        st.header("📥 Văn bản gửi cho bạn")
        df_in = load_sheet_data("docs_in")
        
        if not df_in.empty and 'receiver' in df_in.columns:
            # Lọc: Người nhận phải là chính mình
            df_mine = df_in[df_in['receiver'].astype(str) == st.session_state.user_id]
            if not df_mine.empty:
                st.dataframe(df_mine, use_container_width=True)
            else:
                st.info("Hộp thư của bạn đang trống.")
        else:
            st.warning("Dữ liệu trống hoặc thiếu cột 'receiver' trong Sheet 'docs_in'.")

    # --- 📤 SOẠN VĂN BẢN (Gửi cho người khác) ---
    elif menu == "📤 Soạn văn bản GỬI ĐI":
        st.header("📤 Gửi văn bản mới")
        
        # Lấy danh sách người dùng để chọn người nhận
        df_u = load_sheet_data("users")
        list_receivers = df_u['username'].tolist() if not df_u.empty else []

        with st.form("form_gui"):
            to_user = st.selectbox("Chọn người nhận", list_receivers)
            sh = st.text_input("Số hiệu văn bản")
            nd = st.text_area("Nội dung trích yếu")
            
            submit = st.form_submit_button("🚀 GỬI VĂN BẢN")
            
            if submit:
                # Hiển thị thông tin để bạn copy vào Sheets (Vì tính năng ghi tự động cần API bảo mật cao)
                st.success(f"Đã tạo lệnh gửi đến {to_user}!")
                st.info("Bạn hãy copy dòng dưới đây và dán vào Sheet 'docs_in' để người kia thấy:")
                ngay = datetime.now().strftime("%d/%m/%Y")
                st.code(f"{sh}, {ngay}, {st.session_state.user_name}, {nd}, {st.session_state.user_id}, {to_user}")

        st.subheader("📂 Nhật ký văn bản bạn đã gửi")
        df_out = load_sheet_data("docs_in") # Xem lại những gì mình đã gửi trong sheet chung
        if not df_out.empty and 'sender' in df_out.columns:
            df_sent = df_out[df_out['sender'].astype(str) == st.session_state.user_id]
            st.dataframe(df_sent, use_container_width=True)