import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- CẤU HÌNH ---
# Thay SHEET_ID của bạn vào đây (nếu khác)
SHEET_ID = "1UPyO04wZlOtHEIIGN_KHK11I6CslAI0pG2aH6CFECmA"
# Link Apps Script của bạn (link /exec)
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

# Hàm chèn CSS để tạo ảnh nền và làm nổi bật khung nội dung
def add_custom_style_utt():
    # LINK ẢNH NỀN UTT BẠN VỪA GỬI
    image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSjBAMyalgXbQxeREp7VW2F0nWVWgt6gjAhgw&s"

    st.markdown(
         f"""
         <style>
         /* 1. Thiết lập ảnh nền */
         .stApp {{
             background-image: url("{image_url}");
             background-attachment: fixed;
             background-size: cover; /* Phủ kín màn hình */
             background-position: center; /* Căn giữa ảnh */
         }}
         
         /* 2. Thêm lớp phủ mờ màu trắng trên toàn bộ app để chữ dễ đọc hơn */
         .stApp::before {{
             content: "";
             position: absolute;
             top: 0; left: 0; width: 100%; height: 100%;
             background-color: rgba(255, 255, 255, 0.6); /* Độ mờ 60% */
             z-index: -1;
         }}

         /* 3. Làm cho các khung Form, DataFrame, Tabs... có nền trắng đục nổi bật */
         [data-testid="stForm"], .stDataFrame, [data-testid="stTabContent"] {{
             background-color: rgba(255, 255, 255, 0.95); /* Độ đục 95% */
             border-radius: 15px;
             padding: 25px;
             box-shadow: 0 4px 15px rgba(0,0,0,0.1); /* Hiệu ứng đổ bóng nhẹ */
         }}
         
         /* 4. Tùy chỉnh màu chữ tiêu đề cho hợp với nền */
         h1, h2, h3, .stSubheader, [data-testid="stMarkdownContainer"] h1 {{
             color: #004080 !important; /* Màu xanh đậm truyền thống của trường */
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Gọi hàm để hiển thị nền và style
add_custom_style_utt()


if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 ĐĂNG NHẬP", "📝 TẠO TÀI KHOẢN MỚI"])
    
    with tab1:
        st.subheader("Chào mừng bạn quay trở lại")
        u = st.text_input("Tên đăng nhập", key="l_u")
        p = st.text_input("Mật khẩu", type="password", key="l_p")
        if st.button("Xác nhận vào hệ thống"):
            df_u = load_data("users")
            if not df_u.empty:
                # Xử lý ID và Password là chuỗi để tránh lỗi
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
        st.subheader("Tham gia hệ thống quản lý")
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            r_u = st.text_input("Username *", key="reg_u")
            r_f = st.text_input("Họ và Tên *", key="reg_f")
            r_id = st.text_input("Mã định danh (MSSV/MSGV) *", key="reg_id")
        with c_r2:
            r_role = st.selectbox("Chức vụ *", ["Sinh viên", "Giảng viên", "Nhà trường"])
            
            # LOGIC ẨN HIỆN LỚP
            r_c = ""
            if r_role == "Sinh viên":
                r_c = st.text_input("Lớp *", key="reg_c", placeholder="Ví dụ: 22DTH1")
            else:
                r_c = "Cán bộ" # Giá trị mặc định cho Cán bộ/Giảng viên
                
            r_p = st.text_input("Mật khẩu *", type="password", key="reg_p")
            r_cp = st.text_input("Xác nhận mật khẩu *", type="password", key="reg_cp")
        
        if st.button("Đăng ký tài khoản"):
            # KIỂM TRA NOT NULL
            if not (r_u and r_f and r_id and r_p and r_c):
                st.error("❌ Bạn cần điền đầy đủ thông tin vào các ô có dấu (*)")
            elif r_p != r_cp:
                st.error("❌ Mật khẩu xác nhận không khớp nhau!")
            else:
                payload = {
                    "type": "register",
                    "username": r_u, "password": r_p, "fullname": r_f,
                    "id_code": r_id, "role": r_role, "class_name": r_c
                }
                try:
                    res = requests.post(WEB_APP_URL, json=payload)
                    if res.status_code == 200:
                        st.success("🎉 Đăng ký thành công! Hãy quay lại tab Đăng nhập.")
                except: st.error("Lỗi kết nối!")

# --- GIAO DIỆN CHÍNH SAU ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.info(f"Quyền: {st.session_state.user_role}\n\nID: {st.session_state.id_code}")
    if st.session_state.user_role == "Sinh viên":
        st.sidebar.info(f"🏫 Lớp: {st.session_state.user_class}")
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("CHỨC NĂNG", ["📥 VĂN BẢN ĐẾN", "📤 SOẠN VĂN BẢN ĐI"])

    # 1. PHẦN VĂN BẢN ĐẾN (Đọc từ tab doc_in với tiêu đề Anh)
    if menu == "📥 VĂN BẢN ĐẾN":
        st.header("📥 Hộp thư văn bản đến")
        df_in = load_data("doc_in")
        if not df_in.empty:
            # Lọc theo receiver_id của người đang đăng nhập
            # Sử dụng cột header tiếng Anh 'receiver_id'
            df_mine = df_in[df_in['receiver_id'].astype(str) == st.session_state.id_code]
            st.dataframe(df_mine, use_container_width=True)
        else: st.info("Hộp thư trống.")

    # 2. PHẦN VĂN BẢN ĐI (Ghi song song vào doc_out và doc_in)
    elif menu == "📤 SOẠN VĂN BẢN ĐI":
        st.header("📤 Soạn thảo văn bản đi")
        with st.form("form_send"):
            col1, col2 = st.columns(2)
            with col1:
                target_id = st.text_input("Mã ID người nhận *", placeholder="Nhập MSSV/MSGV người nhận")
            with col2:
                loai = st.selectbox("Loại văn bản", ["Công văn", "Đơn từ", "Thông báo", "Khác"])
            
            note = st.text_input("Chú thích (Ghi chú)")
            content = st.text_area("Nội dung văn bản muốn gửi *", height=200)
            
            # Phần add file (Giống ảnh mẫu)
            uploaded_file = st.file_uploader("📎 Đính kèm tệp", type=["pdf", "docx", "jpg", "png", "zip"])
            
            if st.form_submit_button("🚀 GỬI NGAY"):
                if not (target_id and content):
                    st.error("❌ Thiếu thông tin người nhận hoặc nội dung!")
                else:
                    payload = {
                        "type": "send_dual",
                        "date_sent": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "sender_name": st.session_state.user_name,
                        "sender_id": st.session_state.id_code,
                        "receiver_id": target_id,
                        "doc_type": loai,
                        "note": note,
                        "content": content,
                        "file_name": uploaded_file.name if uploaded_file else "Không có"
                    }
                    try:
                        res = requests.post(WEB_APP_URL, json=payload)
                        if res.status_code == 200:
                            st.success(f"✅ Đã gửi thành công tới ID {target_id}!")
                            st.balloons()
                    except: st.error("Lỗi kết nối!")