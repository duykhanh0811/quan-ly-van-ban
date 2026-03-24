import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
# Nhấn nút 'Gửi' trong Google Form, chọn biểu tượng Link để lấy link này
LINK_FORM_GUI = "https://docs.google.com/forms/d/e/XXXXX/viewform" 

def load_data(sheet_name):
    # Dùng link export CSV là cách nhanh nhất và không cần quyền bảo mật cao
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={sheet_name}"
    try:
        # Thêm timestamp để ép Google cập nhật dữ liệu mới liên tục
        return pd.read_csv(url + f"&cache={datetime.now().timestamp()}")
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Văn bản Nội bộ", layout="wide")

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG")
    u = st.text_input("Tên đăng nhập (username)")
    p = st.text_input("Mật khẩu", type="password")
    
    if st.button("Xác nhận đăng nhập"):
        df_u = load_data("users")
        if not df_u.empty:
            # Lọc tài khoản
            user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = user.iloc[0]['fullname']
                st.session_state.user_id = u
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")
        else:
            st.error("⚠️ Lỗi: Không tìm thấy sheet 'users' hoặc file chưa được chia sẻ công khai.")

# --- SAU KHI ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư ĐẾN", "📤 GỬI VĂN BẢN MỚI"])
    
    if st.sidebar.button("Thoát"):
        st.session_state.logged_in = False
        st.rerun()

    # --- CHỨC NĂNG HỘP THƯ ĐẾN ---
    if menu == "📥 Hộp thư ĐẾN":
        st.header(f"📥 Văn bản dành riêng cho {st.session_state.user_name}")
        df_in = load_data("docs_in")
        
        if not df_in.empty:
            # LƯU Ý: Tên cột 'Người nhận' phải khớp chính xác với câu hỏi trong Google Form
            # Ở đây mình lọc theo username (user_id) để đảm bảo tính riêng tư
            if 'Người nhận' in df_in.columns:
                df_mine = df_in[df_in['Người nhận'].astype(str) == st.session_state.user_id]
                if not df_mine.empty:
                    st.dataframe(df_mine, use_container_width=True)
                else:
                    st.info("Hộp thư của bạn hiện đang trống.")
            else:
                st.warning("Hệ thống chưa tìm thấy cột 'Người nhận' trong dữ liệu.")
        else:
            st.write("Chưa có dữ liệu văn bản.")

    # --- CHỨC NĂNG GỬI VĂN BẢN ---
    elif menu == "📤 GỬI VĂN BẢN MỚI":
        st.header("📤 Soạn thảo văn bản gửi đi")
        st.info("Nhấn nút dưới đây để gửi văn bản. Dữ liệu sẽ tự động chuyển đến đúng người nhận.")
        
        # Nút bấm mở Form gửi
        st.link_button("👉 MỞ FORM SOẠN VĂN BẢN", LINK_FORM_GUI)
        
        st.divider()
        st.subheader("📂 Nhật ký văn bản bạn đã gửi")
        df_all = load_data("docs_in")
        if not df_all.empty and 'Người gửi' in df_all.columns:
            df_sent = df_all[df_all['Người gửi'].astype(str) == st.session_state.user_id]
            st.dataframe(df_sent, use_container_width=True)