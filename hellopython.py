import streamlit as st
import pandas as pd
from datetime import datetime

# --- KẾT NỐI DỮ LIỆU ---
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
LINK_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=users"
LINK_IN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_in"
LINK_OUT = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=docs_out"

def load_data(link):
    try: return pd.read_csv(link)
    except: return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Văn bản Nội bộ", layout="wide")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🔐 HỆ THỐNG GỬI NHẬN VĂN BẢN BẢO MẬT")
    u = st.text_input("Tên đăng nhập")
    p = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        df_u = load_data(LINK_USERS)
        if not df_u.empty:
            user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = user.iloc[0]['fullname']
                st.session_state.user_id = u 
                st.rerun()
            else: st.error("Sai tài khoản!")

# --- SAU KHI ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 Hộp thư ĐẾN (Được gửi cho bạn)", "📤 Văn bản ĐI (Bạn đã gửi)"])
    if st.sidebar.button("Thoát"):
        st.session_state.logged_in = False
        st.rerun()

    # Lấy danh sách tất cả người dùng để chọn người nhận
    df_all_users = load_data(LINK_USERS)
    list_users = df_all_users['username'].tolist() if not df_all_users.empty else []

    # --- 📥 VĂN BẢN ĐẾN (Chỉ hiện văn bản gửi ĐẾN mình) ---
    if menu == "📥 Hộp thư ĐẾN (Được gửi cho bạn)":
        st.header("📥 Văn bản gửi cho bạn")
        df_all_in = load_data(LINK_IN)
        
        if not df_all_in.empty and 'receiver' in df_all_in.columns:
            # LỌC: Chỉ hiện văn bản có receiver == username của mình
            df_mine = df_all_in[df_all_in['receiver'].astype(str) == st.session_state.user_id]
            st.dataframe(df_mine, use_container_width=True)
        else:
            st.info("Hộp thư của bạn đang trống.")

    # --- 📤 VĂN BẢN ĐI (Soạn và gửi cho người khác) ---
    elif menu == "📤 Văn bản ĐI (Bạn đã gửi)":
        st.header("📤 Gửi văn bản cho đồng nghiệp")
        
        with st.expander("🆕 SOẠN VĂN BẢN MỚI", expanded=True):
            with st.form("send_form"):
                target_user = st.selectbox("Chọn người nhận", list_users)
                so_hieu = st.text_input("Số hiệu/Tiêu đề")
                noidung = st.text_area("Nội dung gửi đi")
                
                if st.form_submit_button("🚀 Gửi ngay"):
                    # Ghi chú: Dữ liệu này bạn nên copy vào sheet 'docs_in' của Google Sheets 
                    # để người nhận thấy được bên phía họ.
                    st.success(f"Đã tạo yêu cầu gửi cho: {target_user}")
                    st.code(f"Số hiệu: {so_hieu} | Người gửi: {st.session_state.user_id} | Người nhận: {target_user}")
                    st.info("Hãy dán dòng này vào Google Sheets (Sheet 'docs_in') để hoàn tất gửi.")

        st.subheader("📂 Nhật ký bạn đã gửi")
        df_all_out = load_data(LINK_OUT)
        if not df_all_out.empty and 'sender' in df_all_out.columns:
            # LỌC: Chỉ hiện văn bản do chính mình gửi đi (sender == username)
            df_my_sent = df_all_out[df_all_out['sender'].astype(str) == st.session_state.user_id]
            st.dataframe(df_my_sent, use_container_width=True)