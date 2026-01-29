import streamlit as st
import pandas as pd
import os
import hashlib

USER_FILE = "data/users.csv"

# -------------------- UTILS --------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_store():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(USER_FILE):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USER_FILE, index=False)

def load_users():
    init_user_store()
    return pd.read_csv(USER_FILE)

def save_user(username, password):
    users = load_users()
    users.loc[len(users)] = [username, hash_password(password)]
    users.to_csv(USER_FILE, index=False)

# -------------------- UI STYLES --------------------
st.markdown("""
<style>
/* Center auth container */
.auth-container {
    max-width: 420px;
    margin: auto;
    padding: 2.5rem;
    background: rgba(2,6,23,0.9);
    border: 1px solid #1f2937;
    border-radius: 22px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.45);
    backdrop-filter: blur(14px);
}

/* Title */
.auth-title {
    text-align: center;
    font-size: 1.9rem;
    font-weight: 800;
    background: linear-gradient(90deg,#38bdf8,#818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}

.auth-subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 1.8rem;
    font-size: 0.95rem;
}

/* Inputs */
.stTextInput input {
    background: #020617;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 12px;
    color: #f9fafb;
}

.stTextInput input:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.25);
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg,#38bdf8,#6366f1);
    color: #020617;
    font-weight: 800;
    border-radius: 16px;
    padding: 0.9rem;
    border: none;
    transition: all 0.25s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(56,189,248,0.45);
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 700;
    color: #9ca3af;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #38bdf8;
    border-bottom: 3px solid #38bdf8;
}
</style>
""", unsafe_allow_html=True)

# -------------------- LOGIN --------------------
def login():
    if "user" in st.session_state:
        return

    st.markdown("""
    <div class="auth-container">
        <div class="auth-title">🔐 Secure Access</div>
        <div class="auth-subtitle">Login or create an account to continue</div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    # -------- LOGIN TAB --------
    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", use_container_width=True):
            users = load_users()
            hashed = hash_password(password)

            valid = (
                (users["username"] == username) &
                (users["password"] == hashed)
            ).any()

            if valid:
                st.session_state.user = username
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    # -------- REGISTER TAB --------
    with tab_register:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Create Account", use_container_width=True):
            users = load_users()

            if new_user.strip() == "":
                st.error("Username cannot be empty")
            elif new_user in users["username"].values:
                st.error("Username already exists")
            elif len(new_pass) < 4:
                st.error("Password must be at least 4 characters")
            elif new_pass != confirm:
                st.error("Passwords do not match")
            else:
                save_user(new_user, new_pass)
                st.success("🎉 Registration successful. Please login.")

    st.markdown("</div>", unsafe_allow_html=True)
