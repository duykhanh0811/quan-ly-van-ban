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

# --- ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🏫 HỆ THỐNG VĂN BẢN UTT")
    u = st.text_input("Tên đăng nhập")
    p = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        df_u = load_data("users")
        user_match = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
        if not user_match.empty:
            st.session_state.logged_in = True
            st.session_state.user_name = user_match.iloc[0]['fullname']
            st.session_state.user_role = user_match.iloc[0]['role'] # Lấy vai trò (Sinh viên/Giáo viên...)
            st.session_state.id_code = str(user_match.iloc[0]['id_code']).strip().upper()
            st.rerun()
        else: st.error("Sai tài khoản!")
else:
    # --- GIAO DIỆN CHÍNH ---
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.info(f"Vai trò: {st.session_state.user_role}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư văn bản đến")
        df_in = load_data("doc_in")
        if not df_in.empty:
            df_mine = df_in[df_in['receiver_id'].astype(str).str.upper() == st.session_state.id_code].copy()
            if not df_mine.empty:
                for i, row in df_mine.iterrows():
                    with st.expander(f"✉️ Từ: {row['sender_name']} ({row['date_sent']})"):
                        st.write(f"**Nội dung:** {row['content']}")
                        link_file = str(row['file_name']).strip()
                        if link_file.startswith("http"):
                            st.link_button("📂 MỞ TỆP ĐÍNH KÈM", link_file)
            else: st.info("Không có văn bản nào.")

    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Soạn thảo văn bản")
        df_all_users = load_data("users")
        
        # --- LOGIC PHÂN QUYỀN GỬI ---
        # 1. Nếu là Sinh viên: Chỉ hiện danh sách Giáo viên và Nhà trường
        if st.session_state.user_role == "Sinh viên":
            allowed_users = df_all_users[df_all_users['role'].isin(["Giáo viên", "Nhà trường"])]
            st.warning("💡 Bạn đang gửi văn bản với tư cách Sinh viên (Chỉ gửi cho GV/Nhà trường)")
            
        # 2. Nếu là Nhà trường: Hiện danh sách Giáo viên và Sinh viên
        elif st.session_state.user_role == "Nhà trường":
            allowed_users = df_all_users[df_all_users['role'].isin(["Giáo viên", "Sinh viên"])]
            st.success("💡 Bạn đang gửi văn bản với tư cách Ban Quản lý/Nhà trường")
            
        # 3. Nếu là Giáo viên: Cho phép gửi cho cả Sinh viên và Nhà trường
        else:
            allowed_users = df_all_users[df_all_users['role'] != "Giáo viên"]
            
        # Tạo danh sách chọn người nhận (Tên - ID)
        user_list = [f"{row['fullname']} ({row['id_code']})" for i, row in allowed_users.iterrows()]
        
        with st.form("send_form", clear_on_submit=True):
            selected_receiver = st.selectbox("Chọn người nhận *", options=user_list)
            msg = st.text_area("Nội dung văn bản *")
            up_file = st.file_uploader("Đính kèm tệp")
            
            if st.form_submit_button("🚀 GỬI VĂN BẢN"):
                if selected_receiver and msg:
                    # Tách lấy mã ID từ chuỗi "Tên (ID)"
                    target_id = selected_receiver.split('(')[-1].replace(')', '').strip().upper()
                    
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
                    requests.post(WEB_APP_URL, json=payload)
                    st.success(f"✅ Đã gửi thành công tới {selected_receiver}!")
                else: st.error("Vui lòng điền đủ thông tin!")