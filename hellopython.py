import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CẤU HÌNH ---
# Thay SHEET_ID của bạn vào đây
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
# Link Apps Script bạn đã tạo (link /exec)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwKjL7c8sDm-mJwKlUuOS1K4f5n6EW_AdaUzBI0WLFSE6pJbEwRnhGhugrs0qaIo6fDFg/exec"

def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        return df.fillna("")
    except:
        return pd.DataFrame()

st.set_page_config(page_title="Hệ thống Quản lý Văn bản", layout="wide")

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ (TAB 1 & TAB 2) ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 ĐĂNG NHẬP", "📝 TẠO TÀI KHOẢN MỚI"])
    
    with tab1:
        st.title("Hệ thống Quản lý Nội bộ")
        u = st.text_input("Tên đăng nhập", key="login_u")
        p = st.text_input("Mật khẩu", type="password", key="login_p")
        if st.button("Xác nhận đăng nhập"):
            df_u = load_data("users")
            if not df_u.empty:
                user = df_u[(df_u['username'].astype(str) == u) & (df_u['password'].astype(str) == p)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_id = u
                    st.session_state.user_name = user.iloc[0]['fullname']
                    st.session_state.user_role = user.iloc[0].get('role', 'N/A')
                    st.session_state.user_class = user.iloc[0].get('class_name', 'N/A')
                    st.session_state.id_code = user.iloc[0].get('id_code', 'N/A')
                    st.rerun()
                else: st.error("Sai tài khoản hoặc mật khẩu!")

    with tab2:
        st.title("Đăng ký thành viên")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            r_u = st.text_input("Tên đăng nhập *", key="reg_u")
            r_f = st.text_input("Họ và Tên *", key="reg_f")
            r_id = st.text_input("Mã định danh (MSSV/MSGV) *", key="reg_id")
        
        with col_r2:
            r_role = st.selectbox("Chức vụ *", ["Sinh viên", "Giảng viên", "Nhà trường"], key="reg_role")
            
            # LOGIC ẨN HIỆN: Chỉ hiện lớp nếu là Sinh viên
            r_c = ""
            if r_role == "Sinh viên":
                r_c = st.text_input("Lớp (Ví dụ: 22DTH1) *", key="reg_c")
            else:
                r_c = "Cán bộ" # Giá trị mặc định cho Giảng viên/Nhà trường
                
            r_p = st.text_input("Mật khẩu *", type="password", key="reg_p")
            r_cp = st.text_input("Xác nhận mật khẩu *", type="password", key="reg_cp")
        
        if st.button("Đăng ký ngay"):
            # KIỂM TRA NOT NULL (Không để trống)
            if not (r_u and r_f and r_id and r_p and r_c):
                st.warning("⚠️ Vui lòng điền đầy đủ các thông tin bắt buộc!")
            elif r_p != r_cp:
                st.error("❌ Mật khẩu xác nhận không khớp!")
            else:
                payload = {
                    "type": "register",
                    "username": r_u, "password": r_p, "fullname": r_f,
                    "id_code": r_id, "role": r_role, "class_name": r_c
                }
                try:
                    res = requests.post(WEB_APP_URL, json=payload)
                    if res.status_code == 200:
                        st.success("🎉 Đăng ký thành công! Mời bạn quay lại tab Đăng nhập.")
                except: st.error("Lỗi kết nối!")

# --- GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.write(f"🏷️ **Chức vụ:** {st.session_state.user_role}")
    if st.session_state.user_role == "Sinh viên":
        st.sidebar.write(f"🏫 **Lớp:** {st.session_state.user_class}")
    st.sidebar.write(f"🆔 **ID:** {st.session_state.id_code}")
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("MENU CHỨC NĂNG", ["📂 Danh sách văn bản", "➕ Tiếp nhận văn bản mới"])

    if menu == "📂 Danh sách văn bản":
        st.header("📥 Văn bản đến của bạn")
        df_in = load_data("docs_in")
        if not df_in.empty:
            # Lọc văn bản gửi cho receiver là user_id của bạn
            df_mine = df_in[df_in['receiver'].astype(str) == st.session_state.user_id]
            st.dataframe(df_mine, use_container_width=True)
        else: st.info("Hiện chưa có văn bản nào.")

    elif menu == "➕ Tiếp nhận văn bản mới":
        st.header("📑 THÊM MỚI VĂN BẢN ĐẾN")
        df_u = load_data("users")
        list_users = df_u['username'].tolist() if not df_u.empty else []

        with st.form("form_chuyen_nghiep"):
            c1, c2 = st.columns(2)
            with c1: sh = st.text_input("Số Ký hiệu", placeholder="Ví dụ: 123/UBND-VP")
            with c2: ngay = st.date_input("Ngày nhận", datetime.now()).strftime("%d/%m/%Y")
            
            co_quan = st.text_input("Cơ quan gửi")
            nd = st.text_area("Trích yếu nội dung văn bản")
            
            c3, c4 = st.columns(2)
            with c3: loai = st.selectbox("Loại văn bản", ["Công văn", "Nghị quyết", "Quyết định", "Thông báo"])
            with c4: bao_mat = st.selectbox("Độ bảo mật", ["Thường", "Mật", "Tối mật"])
            
            c5, c6 = st.columns(2)
            with c5: target = st.selectbox("Chuyển cho (Người nhận)", list_users)
            with c6: trang_thai = st.selectbox("Trạng thái", ["Chờ xử lý", "Đang xử lý", "Hoàn thành"])
            
            if st.form_submit_button("💾 LƯU VĂN BẢN"):
                if not (sh and co_quan and nd):
                    st.error("❌ Không được để trống Số hiệu, Cơ quan hoặc Trích yếu!")
                else:
                    payload = {
                        "type": "send", "so_hieu": sh, "ngay": ngay, "co_quan": co_quan,
                        "nd": nd, "loai": loai, "bao_mat": bao_mat, "trang_thai": trang_thai,
                        "sender": st.session_state.user_id, "receiver": target
                    }
                    try:
                        requests.post(WEB_APP_URL, json=payload)
                        st.success("✅ Đã ghi nhận văn bản vào hệ thống thành công!")
                    except: st.error("Lỗi gửi dữ liệu!")