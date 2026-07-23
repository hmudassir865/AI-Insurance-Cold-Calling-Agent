import streamlit as st


def show():
    st.markdown(
        """
    <style>
        .login-container {
            max-width: 400px;
            margin: 8rem auto 2rem auto;
            padding: 2.5rem;
            background: #FFFFFF;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            border: 1px solid #E2E8F0;
        }
        .login-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0F172A;
            text-align: center;
            margin-bottom: 0.25rem;
        }
        .login-subtitle {
            font-size: 0.85rem;
            color: #64748B;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .login-error {
            background: #FEF2F2;
            border: 1px solid #FECACA;
            color: #991B1B;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }
        .login-success {
            background: #F0FDF4;
            border: 1px solid #BBF7D0;
            color: #065F46;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">📞 AI Cold Calling</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-subtitle">Health Insurance Agent Platform</div>',
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="admin@ncai.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🔐 Sign In", type="primary", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Email and password are required")
                else:
                    with st.spinner("Authenticating..."):
                        try:
                            from utils.api_client import login as api_login
                            result = api_login(email, password)
                            st.session_state.access_token = result["access_token"]
                            st.session_state.refresh_token = result["refresh_token"]
                            st.session_state.user = result["user"]
                            st.session_state.authenticated = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Login failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div style="text-align:center;margin-top:1rem;font-size:0.8rem;color:#94A3B8;">'
            "v2.0.0 — Production Ready"
            "</div>",
            unsafe_allow_html=True,
        )
