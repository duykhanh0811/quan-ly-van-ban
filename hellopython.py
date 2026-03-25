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
        df.columns = df.columns.str.strip()
        return df.fillna("")
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Văn bản UTT", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ĐĂNG NHẬP / ĐĂNG KÝ (Giữ nguyên logic cũ) ---
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
                    st.session_state.logged_in = True
                    st.session_state.user_name = user_match.iloc[0]['fullname']
                    st.session_state.id_code = str(user_match.iloc[0]['id_code']).strip().upper()
                    st.rerun()
                else: st.error("Sai tài khoản!")

    with tab2:
        st.subheader("Tạo tài khoản")
        r_u = st.text_input("Username *", key="reg_u")
        r_f = st.text_input("Họ Tên *")
        r_id = st.text_input("Mã ID *")
        r_p = st.text_input("Mật khẩu *", type="password")
        if st.button("Đăng ký"):
            payload = {"type": "register", "username": r_u, "password": r_p, "fullname": r_f, "id_code": r_id.strip().upper(), "role": "Sinh viên", "class_name": "N/A"}
            requests.post(WEB_APP_URL, json=payload)
            st.success("Xong!")

# --- GIAO DIỆN CHÍNH ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.write(f"ID: {st.session_state.id_code}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư văn bản đến")
        df_in = load_data("doc_in")
        if not df_in.empty:
            df_in['receiver_id'] = df_in['receiver_id'].astype(str).str.strip().str.upper()
            df_mine = df_in[df_in['receiver_id'] == st.session_state.id_code]
            
            if not df_mine.empty:
                # TỐI ƯU: Biến cột file_name thành Link có thể nhấn được
                st.data_editor(
                    df_mine,
                    column_config={
                        "file_name": st.column_config.LinkColumn(
                            "Tệp đính kèm",
                            help="Nhấn để mở file",
                            validate="^http", # Chỉ kích hoạt nếu là link http
                            display_text="Xem file" # Hiện chữ 'Xem file' thay vì link dài
                        ),
                    },
                    hide_index=True,
                    use_container_width=True,
                    disabled=True # Chỉ cho xem, không cho sửa trực tiếp trong bảng
                )
            else: st.info("Hộp thư trống.")
        else: st.info("Chưa có dữ liệu.")

    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Soạn thảo văn bản đi")
        with st.form("form_send"):
            target_id = st.text_input("Mã ID người nhận *").strip().upper()
            content = st.text_area("Nội dung *")
            # Ở phiên bản này, bạn hãy dán Link Drive của file vào đây thay vì tải file lên trực tiếp
            file_url = st.text_input("Dán link file đính kèm (Google Drive/Image Link)", placeholder="https://drive.google.com/...")
            
            if st.form_submit_button("🚀 GỬI"):
                if target_id and content:
                    payload = {
                        "type": "send_dual",
                        "date_sent": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "sender_name": st.session_state.user_name,
                        "sender_id": st.session_state.id_code,
                        "receiver_id": target_id,
                        "doc_type": "Văn bản", "note": "", "content": content,
                        "file_name": file_url if file_url else "Không có" # Lưu Link thay vì tên file
                    }
                    requests.post(WEB_APP_URL, json=payload)
                    st.success(f"Đã gửi thành công!")