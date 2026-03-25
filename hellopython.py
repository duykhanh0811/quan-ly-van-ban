import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CẤU HÌNH ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwKjL7c8sDm-mJwKlUuOS1K4f5n6EW_AdaUzBI0WLFSE6pJbEwRnhGhugrs0qaIo6fDFg/exec"

def load_data(sheet_name):
    # Thêm tham số cache_drops để luôn lấy dữ liệu mới nhất
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        # Làm sạch tên cột (xóa khoảng trắng thừa)
        df.columns = df.columns.str.strip()
        return df.fillna("")
    except Exception as e:
        st.error(f"Lỗi tải bảng {sheet_name}: {e}")
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Quản lý Văn bản UTT", layout="wide")

# Khởi tạo session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 ĐĂNG NHẬP", "📝 TẠO TÀI KHOẢN"])
    
    with tab1:
        st.subheader("Đăng nhập hệ thống")
        u = st.text_input("Tên đăng nhập", key="login_user")
        p = st.text_input("Mật khẩu", type="password", key="login_pass")
        
        if st.button("Vào hệ thống"):
            df_u = load_data("users")
            if not df_u.empty:
                # Kiểm tra tài khoản
                user_match = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                
                if not user_match.empty:
                    try:
                        # Lưu thông tin vào session
                        st.session_state.logged_in = True
                        st.session_state.user_name = user_match.iloc[0]['fullname']
                        st.session_state.user_role = user_match.iloc[0]['role']
                        st.session_state.id_code = str(user_match.iloc[0]['id_code'])
                        st.rerun()
                    except KeyError as e:
                        st.error(f"Thiếu cột trong file Sheets: {e}. Vui lòng kiểm tra lại Hàng 1 của tab users.")
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")

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
                res = requests.post(WEB_APP_URL, json=payload)
                if res.status_code == 200:
                    st.success("🎉 Đăng ký thành công! Hãy chuyển sang tab Đăng nhập.")
            else:
                st.error("Vui lòng điền đủ thông tin!")

# --- GIAO DIỆN CHÍNH SAU ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.info(f"Quyền: {st.session_state.user_role}\nID: {st.session_state.id_code}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư văn bản đến")
        df_in = load_data("doc_in")
        if not df_in.empty:
            # Lọc văn bản gửi cho mình
            df_mine = df_in[df_in['receiver_id'].astype(str) == st.session_state.id_code]
            if not df_mine.empty:
                st.dataframe(df_mine, use_container_width=True)
            else:
                st.info("Bạn chưa nhận được văn bản nào.")
        else:
            st.info("Hộp thư hiện đang trống.")

    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Thêm mới Văn bản đi")
        with st.form("form_send"):
            col_a, col_b = st.columns(2)
            with col_a:
                target_id = st.text_input("Mã ID người nhận *", placeholder="Nhập MSSV/MSGV")
            with col_b:
                loai = st.selectbox("Loại văn bản", ["Công văn", "Thông báo", "Quyết định", "Khác"])
            
            note = st.text_input("Chú thích")
            content = st.text_area("Nội dung văn bản *", height=200)
            file = st.file_uploader("📎 Đính kèm tệp", type=["pdf", "png", "jpg"])
            
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
                    requests.post(WEB_APP_URL, json=payload)
                    st.success("✅ Đã gửi thành công!")
                else:
                    st.error("Vui lòng điền đủ Mã ID người nhận và Nội dung!")