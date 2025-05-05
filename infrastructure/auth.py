# infrastructure/auth.py
import streamlit as st
from supabase import create_client

def setup_auth():
    if 'supabase' not in st.session_state:
        try:
            st.session_state.supabase = create_client(
                st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"]
            )
        except Exception as e:
            st.error(f"Supabase init error: {e}")
            return False

    if 'user' in st.session_state:
        return True

    st.title("DANI - Login")
    tab1, tab2 = st.tabs(["Login","Sign Up"])
    with tab1:
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                r = st.session_state.supabase.auth.sign_in_with_password({"email":email,"password":pwd})
                st.session_state.user = r.user
                return True
            except Exception as e:
                st.error(f"Login failed: {e}")
    with tab2:
        email = st.text_input("Email", key="su")
        pwd = st.text_input("Password", type="password", key="sup")
        pwdc= st.text_input("Confirm", type="password")
        if st.button("Sign Up"):
            if pwd!=pwdc:
                st.error("Mismatch")
            else:
                try:
                    st.session_state.supabase.auth.sign_up({"email":email,"password":pwd})
                    st.success("Check email")
                except Exception as e:
                    st.error(f"Sign up error: {e}")
    st.markdown("---")
    link_email = st.text_input("Magic link email")
    if st.button("Send Magic Link"):
        try:
            st.session_state.supabase.auth.sign_in_with_otp({"email":link_email})
            st.success("Link sent")
        except Exception as e:
            st.error(f"Magic link error: {e}")
    return False
