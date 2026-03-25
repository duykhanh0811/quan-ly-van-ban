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
            st.session_state.id_code = str(user_match.iloc[0]['id_code']).strip().upper()
            st.rerun()
        else: st.error("Sai tài khoản!")
else:
    # --- GIAO DIỆN CHÍNH ---
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.write(f"ID: {st.session_state.id_code}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Danh sách văn bản gửi cho bạn")
        df_in = load_data("doc_in")
        if not df_in.empty:
            # Lọc văn bản gửi đúng cho ID của bạn
            df_mine = df_in[df_in['receiver_id'].astype(str).str.upper() == st.session_state.id_code].copy()
            
            if not df_mine.empty:
                st.info(f"Bạn có {len(df_mine)} văn bản. Bấm vào để xem và mở file.")
                for i, row in df_mine.iterrows():
                    # Tạo hộp bấm để xem nội dung
                    with st.expander(f"✉️ Thư từ: {row['sender_name']} ({row['date_sent']})"):
                        st.write(f"**Nội dung:** {row['content']}")
                        
                        # KIỂM TRA VÀ TẠO NÚT MỞ FILE
                        link_file = str(row['file_name']).strip()
                        if link_file.startswith("http"):
                            st.link_button("📂 NHẤN ĐỂ MỞ FILE ĐÍNH KÈM", link_file)
                        else:
                            st.warning("Văn bản này không có tệp đính kèm hoặc lỗi link.")
            else: st.info("Hộp thư trống.")
        else: st.info("Hệ thống chưa có dữ liệu.")

    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Gửi văn bản mới")
        with st.form("send_form", clear_on_submit=True):
            receiver = st.text_input("ID người nhận (Ví dụ: 75DCTT21381)").strip().upper()
            msg = st.text_area("Nội dung")
            up_file = st.file_uploader("Đính kèm tệp từ máy")
            
            if st.form_submit_button("🚀 Gửi"):
                if receiver and msg:
                    f_b64, f_name, f_type = None, "Không có", None
                    if up_file:
                        f_b64 = base64.b64encode(up_file.read()).decode()
                        f_name = up_file.name
                        f_type = up_file.type
                    
                    payload = {
                        "type": "send_dual", "date_sent": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "sender_name": st.session_state.user_name, "sender_id": st.session_state.id_code,
                        "receiver_id": receiver, "doc_type": "Văn bản", "note": "", 
                        "content": msg, "file_name": f_name, "file_data": f_b64, "file_type": f_type
                    }
                    requests.post(WEB_APP_URL, json=payload)
                    st.success("Đã gửi thành công!")
                else: st.error("Thiếu thông tin!")