import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CẤU HÌNH ---
# Duy Khánh nhớ thay SHEET_ID và WEB_APP_URL của bạn vào đây
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwKjL7c8sDm-mJwKlUuOS1K4f5n6EW_AdaUzBI0WLFSE6pJbEwRnhGhugrs0qaIo6fDFg/exec"

def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        return df.fillna("")
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Quản lý Văn bản UTT", layout="wide")

# Khởi tạo session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 ĐĂNG NHẬP", "📝 TẠO TÀI KHOẢN"])
    
    with tab1:
        st.subheader("Đăng nhập hệ thống")
        u = st.text_input("Tên đăng nhập", key="login_user")
        p = st.text_input("Mật khẩu", type="password", key="login_pass")
        if st.button("Vào hệ thống"):
            df_u = load_data("users")
            if not df_u.empty:
                # Tìm user khớp user và pass
                user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user.iloc[0]['fullname']
                    st.session_state.user_role = user.iloc[0]['role']
                    st.session_state.id_code = str(user.iloc[0]['id_code'])
                    st.rerun()
                else: st.error("Sai tài khoản hoặc mật khẩu!")

    with tab2:
        st.subheader("Đăng ký thành viên mới")
        c1, c2 = st.columns(2)
        with c1:
            r_u = st.text_input("Tên đăng nhập *", key="reg_u")
            r_f = st.text_input("Họ và Tên *", key="reg_f")
            r_id = st.text_input("Mã định danh (MSSV/MSGV) *", key="reg_id")
        with c2:
            r_role = st.selectbox("Chức vụ *", ["Sinh viên", "Giảng viên", "Nhà trường"])
            r_c = st.text_input("Lớp *") if r_role == "Sinh viên" else "Cán bộ"
            r_p = st.text_input("Mật khẩu *", type="password", key="reg_p")
        
        if st.button("Xác nhận đăng ký"):
            if r_u and r_f and r_id and r_p:
                payload = {
                    "type": "register",
                    "username": r_u, "password": r_p, "fullname": r_f,
                    "id_code": r_id, "role": r_role, "class_name": r_c
                }
                try:
                    requests.post(WEB_APP_URL, json=payload)
                    st.success("🎉 Đăng ký thành công! Hãy chuyển sang tab Đăng nhập.")
                except: st.error("Lỗi kết nối Server!")
            else: st.error("Vui lòng điền đủ thông tin!")

# --- GIAO DIỆN CHÍNH (SAU ĐĂNG NHẬP) ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.info(f"Quyền: {st.session_state.user_role}\nID: {st.session_state.id_code}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    # 1. PHẦN VĂN BẢN ĐẾN (Hộp thư)
    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư văn bản đến")
        df_in = load_data("doc_in")
        if not df_in.empty:
            # Lọc văn bản mà Mã ID người nhận khớp với ID của mình
            df_mine = df_in[df_in['receiver_id'].astype(str) == st.session_state.id_code]
            if not df_mine.empty:
                st.dataframe(df_mine, use_container_width=True)
            else: st.info("Bạn chưa có văn bản nào.")
        else: st.info("Hộp thư hiện đang trống.")

    # 2. PHẦN VĂN BẢN ĐI (Gửi đi)
    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Thêm mới Văn bản đi")
        with st.form("form_send_doc"):
            col_a, col_b = st.columns(2)
            with col_a:
                target_id = st.text_input("Mã ID người nhận *", placeholder="Nhập MSSV/MSGV")
            with col_b:
                loai = st.selectbox("Loại văn bản", ["Công văn", "Thông báo", "Quyết định", "Đơn từ", "Khác"])
            
            note = st.text_input("Chú thích", placeholder="Ghi chú nhanh...")
            content = st.text_area("Nội dung văn bản *", height=200)
            file = st.file_uploader("📎 Đính kèm tệp", type=["pdf", "png", "jpg", "docx"])
            
            if st.form_submit_button("🚀 GỬI VĂN BẢN"):
                if target_id and content:
                    payload = {
                        "type": "send_dual",
                        "date_sent": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "sender_name": st.session_state.user_name,
                        "sender_id": st.session_state.id_code,
                        "receiver_id": target_id,
                        "doc_type": loai,
                        "note": note,
                        "content": content,
                        "file_name": file.name if file else "Không có"
                    }
                    try:
                        requests.post(WEB_APP_URL, json=payload)
                        st.success(f"✅ Đã gửi thành công tới ID: {target_id}!")
                        st.balloons()
                    except: st.error("Lỗi khi gửi văn bản!")
                else: st.error("Vui lòng điền Mã ID người nhận và Nội dung!")