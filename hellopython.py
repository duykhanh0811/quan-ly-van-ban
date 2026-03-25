import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64

# --- CẤU HÌNH ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwKjL7c8sDm-mJwKlUuOS1K4f5n6EW_AdaUzBI0WLFSE6pJbEwRnhGhugrs0qaIo6fDFg/exec"

def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df.fillna("")
    except: return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Văn bản UTT", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    st.title("🏫 HỆ THỐNG VĂN BẢN UTT")
    tab_login, tab_reg = st.tabs(["🔐 ĐĂNG NHẬP", "📝 ĐĂNG KÝ TÀI KHOẢN"])
    
    with tab_login:
        u = st.text_input("Tên đăng nhập", key="login_u")
        p = st.text_input("Mật khẩu", type="password", key="login_p")
        if st.button("Vào hệ thống"):
            df_u = load_data("users")
            if not df_u.empty:
                user_match = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user_match.iloc[0]['fullname']
                    st.session_state.user_role = user_match.iloc[0]['role']
                    st.session_state.id_code = str(user_match.iloc[0]['id_code']).strip().upper()
                    st.rerun()
                else: st.error("Sai tài khoản hoặc mật khẩu!")

    with tab_reg:
        st.subheader("Tạo tài khoản mới")
        with st.form("reg_form"):
            new_u = st.text_input("Tên đăng nhập (Username) *")
            new_f = st.text_input("Họ và Tên *")
            new_id = st.text_input("Mã định danh (MSSV/MSGV) *")
            new_role = st.selectbox("Vai trò *", ["Sinh viên", "Giáo viên", "Nhà trường"])
            new_p = st.text_input("Mật khẩu *", type="password")
            if st.form_submit_button("Xác nhận Đăng ký"):
                if new_u and new_f and new_id and new_p:
                    payload = {
                        "type": "register", "username": new_u, "fullname": new_f,
                        "id_code": new_id.strip().upper(), "role": new_role, 
                        "password": new_p, "class_name": "N/A"
                    }
                    requests.post(WEB_APP_URL, json=payload)
                    st.success("🎉 Đăng ký thành công! Hãy qua tab Đăng nhập.")
                else: st.error("Vui lòng điền đầy đủ thông tin!")

# --- GIAO DIỆN SAU KHI ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.info(f"Vai trò: {st.session_state.user_role}")
    
    menu_options = ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"]
    if st.session_state.user_role == "Nhà trường":
        menu_options.append("📊 QUẢN LÝ TỔNG THỂ")
    
    menu = st.sidebar.radio("CHỨC NĂNG", menu_options)
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    # --- 1. VĂN BẢN ĐẾN ---
    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư cá nhân")
        df_in = load_data("doc_in")
        if not df_in.empty:
            df_mine = df_in[df_in['receiver_id'].astype(str).str.upper() == st.session_state.id_code].copy()
            if not df_mine.empty:
                for i, row in df_mine.iterrows():
                    with st.expander(f"✉️ Từ: {row['sender_name']} ({row['date_sent']})"):
                        st.write(f"**Nội dung:** {row['content']}")
                        if str(row['file_name']).startswith("http"):
                            st.link_button("📂 MỞ TỆP ĐÍNH KÈM", row['file_name'])
            else: st.info("Hộp thư cá nhân hiện đang trống.")

    # --- 2. SOẠN VĂN BẢN ĐI ---
    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Gửi văn bản mới")
        df_all_users = load_data("users")
        
        # Phân quyền người nhận
        if st.session_state.user_role == "Sinh viên":
            allowed = df_all_users[df_all_users['role'].isin(["Giáo viên", "Nhà trường"])]
        elif st.session_state.user_role == "Nhà trường":
            allowed = df_all_users[df_all_users['role'].isin(["Giáo viên", "Sinh viên"])]
        else: # Giáo viên
            allowed = df_all_users[df_all_users['role'] != "Giáo viên"]
            
        user_list = [f"{r['fullname']} ({r['id_code']})" for i, r in allowed.iterrows()]
        
        with st.form("send_form", clear_on_submit=True):
            receiver = st.selectbox("Chọn người nhận *", options=user_list)
            msg = st.text_area("Nội dung văn bản *")
            up_file = st.file_uploader("Đính kèm tệp")
            
            if st.form_submit_button("🚀 GỬI"):
                if receiver and msg:
                    target_id = receiver.split('(')[-1].replace(')', '').strip().upper()
                    f_b64, f_name, f_type = None, "Không có", None
                    if up_file:
                        f_b64 = base64.b64encode(up_file.read()).decode()
                        f_name = up_file.name
                        f_type = up_file.type
                    
                    payload = {
                        "type": "send_dual", "date_sent": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "sender_name": st.session_state.user_name, "sender_id": st.session_state.id_code,
                        "receiver_id": target_id, "doc_type": "Văn bản", "note": "", 
                        "content": msg, "file_name": f_name, "file_data": f_b64, "file_type": f_type
                    }
                    with st.spinner("Đang gửi..."):
                        requests.post(WEB_APP_URL, json=payload)
                    st.success(f"✅ Đã gửi tới {receiver}!")
                else: st.error("Thiếu thông tin!")

    # --- 3. QUẢN LÝ TỔNG THỂ (Chỉ Nhà trường) ---
    elif menu == "📊 QUẢN LÝ TỔNG THỂ":
        st.header("📊 Theo dõi văn bản toàn hệ thống")
        t1, t2 = st.tabs(["Văn bản đến (Tổng)", "Văn bản đi (Tổng)"])
        with t1: st.dataframe(load_data("doc_in"), use_container_width=True)
        with t2: st.dataframe(load_data("doc_out"), use_container_width=True)