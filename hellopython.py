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
        return df.fillna("")
    except:
        return pd.DataFrame()

# --- CẤU HÌNH GIAO DIỆN VÀ NỀN ---
st.set_page_config(page_title="Hệ thống Quản lý Văn bản UTT", layout="wide")

def add_custom_style_utt():
    image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSjBAMyalgXbQxeREp7VW2F0nWVWgt6gjAhgw&s"
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("{image_url}");
             background-attachment: fixed;
             background-size: cover;
             background-position: center;
         }}
         .stApp::before {{
             content: "";
             position: absolute;
             top: 0; left: 0; width: 100%; height: 100%;
             background-color: rgba(255, 255, 255, 0.7); 
             z-index: -1;
         }}
         [data-testid="stForm"], .stDataFrame, [data-testid="stTabContent"] {{
             background-color: rgba(255, 255, 255, 0.95);
             border-radius: 15px;
             padding: 20px;
             box-shadow: 0 4px 15px rgba(0,0,0,0.1);
         }}
         h1, h2, h3 {{ color: #004080 !important; }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_custom_style_utt()

# Khởi tạo session state để tránh lỗi AttributeError
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- MÀN HÌNH CHƯA ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 ĐĂNG NHẬP", "📝 TẠO TÀI KHOẢN"])
    
    with tab1:
        u = st.text_input("Tên đăng nhập", key="l_u")
        p = st.text_input("Mật khẩu", type="password", key="l_p")
        if st.button("Xác nhận vào hệ thống"):
            df_u = load_data("users")
            if not df_u.empty:
                user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user.iloc[0]['fullname']
                    st.session_state.user_role = user.iloc[0]['role']
                    st.session_state.id_code = str(user.iloc[0]['id_code'])
                    st.rerun()
                else: st.error("Sai tài khoản hoặc mật khẩu!")

    with tab2:
        st.subheader("Đăng ký thành viên")
        c1, c2 = st.columns(2)
        with c1:
            r_u = st.text_input("Username *", key="reg_u")
            r_f = st.text_input("Họ và Tên *", key="reg_f")
            r_id = st.text_input("Mã định danh (ID) *", key="reg_id")
        with c2:
            r_role = st.selectbox("Chức vụ *", ["Sinh viên", "Giảng viên", "Nhà trường"])
            r_c = st.text_input("Lớp *", key="reg_c") if r_role == "Sinh viên" else "Cán bộ"
            r_p = st.text_input("Mật khẩu *", type="password", key="reg_p")
        
        if st.button("Gửi đăng ký"):
            if r_u and r_f and r_id and r_p:
                payload = {"type": "register", "username": r_u, "password": r_p, "fullname": r_f, "id_code": r_id, "role": r_role, "class_name": r_c}
                requests.post(WEB_APP_URL, json=payload)
                st.success("Đăng ký thành công!")

# --- GIAO DIỆN SAU ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.write(f"ID: {st.session_state.id_code}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("MENU", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư đến")
        df_in = load_data("doc_in")
        if not df_in.empty:
            df_mine = df_in[df_in['receiver_id'].astype(str) == st.session_state.id_code]
            st.dataframe(df_mine, use_container_width=True)
        else: st.info("Hộp thư trống.")

    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Thêm mới Văn bản đi")
        with st.form("form_send"):
            col_a, col_b = st.columns(2)
            with col_a:
                target_id = st.text_input("Mã ID người nhận *")
            with col_b:
                loai = st.selectbox("Loại văn bản", ["Công văn", "Quyết định", "Thông báo", "Khác"])
            
            note = st.text_input("Chú thích")
            content = st.text_area("Văn bản muốn gửi *", height=150)
            file = st.file_uploader("📎 Tải tệp đính kèm", type=["pdf", "png", "jpg"])
            
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
                    st.success("Đã gửi thành công!")
                else: st.error("Vui lòng điền đủ thông tin!")