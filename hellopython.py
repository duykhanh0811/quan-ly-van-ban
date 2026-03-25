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

# --- LOGIC ĐĂNG NHẬP (Giữ nguyên) ---
if not st.session_state.logged_in:
    # ... (Phần code đăng nhập của Duy Khánh) ...
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
else:
    # --- GIAO DIỆN CHÍNH ---
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Danh sách văn bản gửi cho bạn")
        df_in = load_data("doc_in")
        if not df_in.empty:
            df_in['receiver_id'] = df_in['receiver_id'].astype(str).str.strip().str.upper()
            df_mine = df_in[df_in['receiver_id'] == st.session_state.id_code].copy()
            
            if not df_mine.empty:
                # HIỂN THỊ BẢNG THÔNG MINH
                st.data_editor(
                    df_mine,
                    column_config={
                        "content": st.column_config.TextColumn("Nội dung văn bản", width="large"),
                        "file_name": st.column_config.LinkColumn("Tệp đính kèm", display_text="🔗 Mở File"),
                        "date_sent": "Thời gian",
                        "sender_name": "Người gửi"
                    },
                    hide_index=True, use_container_width=True, disabled=True
                )
                
                # Xem chi tiết nội dung khi chọn dòng (Tùy chọn thêm)
                st.divider()
                st.subheader("🔍 Xem nhanh nội dung")
                for i, row in df_mine.iterrows():
                    with st.expander(f"Thư từ {row['sender_name']} - {row['date_sent']}"):
                        st.write(f"**Nội dung:** {row['content']}")
                        if "http" in str(row['file_name']):
                            st.link_button("Mở tệp đính kèm", row['file_name'])
            else: st.info("Bạn không có văn bản nào.")

    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Gửi văn bản mới")
        with st.form("send_form", clear_on_submit=True):
            receiver = st.text_input("Mã ID người nhận (Ví dụ: 75DCTT21381)").strip().upper()
            msg = st.text_area("Nội dung tin nhắn/văn bản")
            up_file = st.file_uploader("Đính kèm tệp")
            
            if st.form_submit_button("🚀 Gửi ngay"):
                if receiver and msg:
                    file_b64, f_name, f_type = None, "Không có tệp", None
                    if up_file:
                        file_b64 = base64.b64encode(up_file.read()).decode()
                        f_name = up_file.name
                        f_type = up_file.type
                    
                    payload = {
                        "type": "send_dual", "date_sent": datetime.now().strftime("%H:%M %d/%m/%Y"),
                        "sender_name": st.session_state.user_name, "sender_id": st.session_state.id_code,
                        "receiver_id": receiver, "doc_type": "Thông báo", "note": "", 
                        "content": msg, "file_name": f_name, "file_data": file_b64, "file_type": f_type
                    }
                    requests.post(WEB_APP_URL, json=payload)
                    st.success("✅ Đã gửi! Người nhận có thể xem được ngay.")
                else: st.error("Vui lòng điền ID và nội dung.")