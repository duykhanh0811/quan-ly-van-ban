import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. KẾT NỐI VÀ KHỞI TẠO DATABASE ---
def init_db():
    conn = sqlite3.connect('university_docs.db')
    c = conn.cursor()
    # Tạo bảng người dùng
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, fullname TEXT)''')
    # Tạo bảng văn bản đến
    c.execute('''CREATE TABLE IF NOT EXISTS docs_in 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, so_hieu TEXT, ngay_den TEXT, noi_gui TEXT, noi_dung TEXT)''')
    # Tạo bảng văn bản đi
    c.execute('''CREATE TABLE IF NOT EXISTS docs_out 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, so_di TEXT, ngay_di TEXT, noi_nhan TEXT, nguoi_ky TEXT, noi_dung TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. CÁC HÀM XỬ LÝ DỮ LIỆU ---
def add_user(username, password, fullname):
    conn = sqlite3.connect('university_docs.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, fullname))
        conn.commit()
        return True
    except:
        return False
    finally: conn.close()

def login_user(username, password):
    conn = sqlite3.connect('university_docs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    data = c.fetchone()
    conn.close()
    return data

# --- 3. GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Hệ thống SQL Đại học", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký tài khoản"])
    
    with tab1:
        u = st.text_input("Tên đăng nhập", key="login_u")
        p = st.text_input("Mật khẩu", type="password", key="login_p")
        if st.button("Đăng nhập"):
            user = login_user(u, p)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_name = user[2]
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu")

    with tab2:
        new_u = st.text_input("Tên đăng nhập mới")
        new_p = st.text_input("Mật khẩu mới", type="password")
        new_f = st.text_input("Họ và tên")
        if st.button("Tạo tài khoản"):
            if add_user(new_u, new_p, new_f):
                st.success("Đăng ký thành công! Hãy quay lại tab Đăng nhập.")
            else:
                st.error("Tên đăng nhập đã tồn tại!")

# --- MÀN HÌNH SAU KHI ĐĂNG NHẬP ---
else:
    st.sidebar.title(f"Chào, {st.session_state.user_name}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("CHỨC NĂNG", ["Văn bản ĐẾN", "Văn bản ĐI"])
    conn = sqlite3.connect('university_docs.db')

    if menu == "Văn bản ĐẾN":
        st.header("📥 Quản lý Văn bản Đến")
        with st.form("in"):
            so = st.text_input("Số hiệu")
            ngay = st.date_input("Ngày nhận")
            gui = st.text_input("Nơi gửi")
            nd = st.text_area("Trích yếu")
            if st.form_submit_button("Lưu vào SQL"):
                pd.io.sql.to_sql(pd.DataFrame([{'so_hieu':so, 'ngay_den':ngay, 'noi_gui':gui, 'noi_dung':nd}]), 
                                 'docs_in', conn, if_exists='append', index=False)
                st.success("Đã lưu vĩnh viễn!")
        
        df = pd.read_sql("SELECT * FROM docs_in", conn)
        st.dataframe(df, use_container_width=True)

    elif menu == "Văn bản ĐI":
        st.header("📤 Quản lý Văn bản Đi")
        with st.form("out"):
            so_di = st.text_input("Số ký hiệu đi")
            ngay_di = st.date_input("Ngày ban hành")
            nhan = st.text_input("Nơi nhận")
            ky = st.text_input("Người ký")
            nd_di = st.text_area("Nội dung")
            if st.form_submit_button("Phát hành"):
                pd.io.sql.to_sql(pd.DataFrame([{'so_di':so_di, 'ngay_di':ngay_di, 'noi_nhan':nhan, 'nguoi_ky':ky, 'noi_dung':nd_di}]), 
                                 'docs_out', conn, if_exists='append', index=False)
                st.success("Đã lưu vào nhật ký SQL!")

        df_out = pd.read_sql("SELECT * FROM docs_out", conn)
        st.dataframe(df_out, use_container_width=True)
    
    conn.close()