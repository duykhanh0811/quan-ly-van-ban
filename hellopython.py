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

st.set_page_config(page_title="Quản lý Văn bản UTT", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🏫 HỆ THỐNG VĂN BẢN UTT")
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
            else: st.error("Sai tài khoản hoặc mật khẩu!")
else:
    # --- GIAO DIỆN CHÍNH ---
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.write(f"ID: {st.session_state.id_code}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư văn bản đến")
        df_in = load_data("doc_in")
        if not df_in.empty:
            df_in['receiver_id'] = df_in['receiver_id'].astype(str).str.strip().str.upper()
            df_mine = df_in[df_in['receiver_id'] == st.session_state.id_code].copy()
            
            if not df_mine.empty:
                st.info(f"Bạn có {len(df_mine)} văn bản mới. Bấm vào từng thư để xem nội dung.")
                for i, row in df_mine.iterrows():
                    # HIỂN THỊ NỘI DUNG NGAY LẬP TỨC KHI BẤM VÀO EXPANDER
                    with st.expander(f"✉️ Từ: {row['sender_name']} | Ngày: {row['date_sent']}"):
                        st.markdown(f"**Loại:** {row['doc_type']}")
                        st.markdown(f"**Nội dung:**")
                        st.info(row['content'])
                        
                        # KIỂM TRA LINK FILE DRIVE
                        f_link = str(row['file_name'])
                        if f_link.startswith("http"):
                            st.link_button("📂 Mở tệp đính kèm", f_link)
                        else:
                            st.caption("ℹ️ Không có tệp đính kèm cho văn bản này.")
            else: st.info("Hộp thư của bạn hiện đang trống.")
        else: st.info("Chưa có dữ liệu văn bản nào trên hệ thống.")

    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Soạn thảo văn bản đi")
        with st.form("send_form", clear_on_submit=True):
            target_id = st.text_input("Mã ID người nhận * (Ví dụ: 75DCTT21381)").strip().upper()
            loai = st.selectbox("Loại văn bản", ["Thông báo", "Công văn", "Đơn từ", "Khác"])
            content = st.text_area("Nội dung văn bản *", height=150)
            up_file = st.file_uploader("📎 Đính kèm tệp từ máy (PDF, Ảnh, Word)")
            
            if st.form_submit_button("🚀 GỬI NGAY"):
                if target_id and content:
                    f_b64, f_name, f_type = None, "Không có tệp", None
                    if up_file:
                        f_b64 = base64.b64encode(up_file.read()).decode()
                        f_name = up_file.name
                        f_type = up_file.type
                    
                    payload = {
                        "type": "send_dual",
                        "date_sent": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "sender_name": st.session_state.user_name,
                        "sender_id": st.session_state.id_code,
                        "receiver_id": target_id,
                        "doc_type": loai, "note": "", "content": content,
                        "file_name": f_name, "file_data": f_b64, "file_type": f_type
                    }
                    
                    with st.spinner('Đang gửi và tải file lên Drive...'):
                        res = requests.post(WEB_APP_URL, json=payload)
                    if res.status_code == 200:
                        st.success(f"✅ Đã gửi thành công tới ID: {target_id}!")
                        st.balloons()
                else: st.error("Vui lòng điền ID người nhận và Nội dung!")