import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CẤU HÌNH ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwKjL7c8sDm-mJwKlUuOS1K4f5n6EW_AdaUzBI0WLFSE6pJbEwRnhGhugrs0qaIo6fDFg/exec"

def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip() # Xóa khoảng trắng ở tiêu đề
        return df.fillna("")
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Quản lý Văn bản UTT", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP (Đã fix lỗi ID trống) ---
if not st.session_state.logged_in:
    st.title("🏫 HỆ THỐNG VĂN BẢN UTT")
    tab1, tab2 = st.tabs(["🔐 ĐĂNG NHẬP", "📝 ĐĂNG KÝ"])
    with tab1:
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("Vào hệ thống"):
            df_u = load_data("users")
            if not df_u.empty:
                user_match = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                if not user_match.empty:
                    # LẤY ID VÀ KIỂM TRA NGAY LẬP TỨC
                    val_id = user_match.iloc[0].get('id_code', "")
                    if str(val_id).strip() == "":
                        st.error("❌ Tài khoản này chưa có Mã ID trong Sheet 'users'. Hãy kiểm tra lại cột id_code!")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_name = user_match.iloc[0]['fullname']
                        st.session_state.user_role = user_match.iloc[0]['role']
                        # Lưu ID ở dạng chữ hoa để so sánh chính xác
                        st.session_state.id_code = str(val_id).strip().upper()
                        st.rerun()
                else: st.error("Sai tài khoản hoặc mật khẩu!")

    with tab2:
        # Giữ nguyên phần đăng ký của bạn...
        st.subheader("Đăng ký thành viên")
        r_u = st.text_input("Username *", key="reg_u")
        r_f = st.text_input("Họ và Tên *", key="reg_f")
        r_id = st.text_input("Mã định danh (ID) *", key="reg_id")
        r_p = st.text_input("Mật khẩu *", type="password", key="reg_p")
        if st.button("Xác nhận đăng ký"):
            payload = {"type": "register", "username": r_u, "password": r_p, "fullname": r_f, "id_code": r_id.strip().upper(), "role": "Sinh viên", "class_name": "N/A"}
            requests.post(WEB_APP_URL, json=payload)
            st.success("Đăng ký thành công!")

# --- GIAO DIỆN CHÍNH (Đã fix lỗi lọc văn bản) ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.markdown(f"**Mã ID:** `{st.session_state.id_code}`")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư văn bản đến")
        df_in = load_data("doc_in") # Lưu ý: tab phải tên là doc_in
        if not df_in.empty:
            # Ép kiểu và chuẩn hóa ID trong Sheet để so sánh
            df_in['receiver_id'] = df_in['receiver_id'].astype(str).str.strip().str.upper()
            df_mine = df_in[df_in['receiver_id'] == st.session_state.id_code]
            
            if not df_mine.empty:
                st.dataframe(df_mine, use_container_width=True)
            else:
                st.info(f"Hộp thư trống (ID đang kiểm tra: {st.session_state.id_code})")
        else: st.info("Chưa có dữ liệu văn bản.")

    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Soạn thảo văn bản đi")
        with st.form("form_send"):
            target_id = st.text_input("Mã ID người nhận *").strip().upper()
            content = st.text_area("Nội dung *")
            if st.form_submit_button("🚀 GỬI"):
                if target_id and content:
                    payload = {
                        "type": "send_dual",
                        "date_sent": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "sender_name": st.session_state.user_name,
                        "sender_id": st.session_state.id_code,
                        "receiver_id": target_id,
                        "doc_type": "Thông báo", "note": "", "content": content, "file_name": "Không có"
                    }
                    requests.post(WEB_APP_URL, json=payload)
                    st.success(f"Đã gửi thành công tới ID: {target_id}")