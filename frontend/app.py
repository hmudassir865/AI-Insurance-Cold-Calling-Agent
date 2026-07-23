import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="AI Health Insurance Cold Calling Agent",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: #F8FAFC;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        border-right: none;
    }

    [data-testid="stSidebar"] .sidebar-title {
        color: #FFFFFF !important;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    [data-testid="stSidebar"] .sidebar-subtitle {
        color: #94A3B8 !important;
        font-size: 0.75rem;
        margin-top: -0.5rem;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: #CBD5E1 !important;
        font-weight: 500;
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        transition: all 0.2s;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.05);
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p {
        font-size: 0.9rem;
    }

    .main-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.03em;
        margin-bottom: 0;
    }

    .main-subheader {
        font-size: 0.9rem;
        color: #64748B;
        margin-top: -0.25rem;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s;
    }

    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }

    .metric-icon {
        font-size: 1.75rem;
        margin-bottom: 0.25rem;
    }

    .metric-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }

    .status-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
    }

    .status-badge.pending { background: #FEF3C7; color: #92400E; }
    .status-badge.interested { background: #D1FAE5; color: #065F46; }
    .status-badge.not_interested { background: #FEE2E2; color: #991B1B; }
    .status-badge.callback { background: #DBEAFE; color: #1E40AF; }
    .status-badge.busy { background: #F3E8FF; color: #6B21A8; }
    .status-badge.completed { background: #D1FAE5; color: #065F46; }
    .status-badge.active { background: #D1FAE5; color: #065F46; }
    .status-badge.draft { background: #F3F4F6; color: #374151; }
    .status-badge.paused { background: #FEF3C7; color: #92400E; }
    .status-badge.failed { background: #FEE2E2; color: #991B1B; }

    .dataframe {
        font-size: 0.85rem;
    }

    .dataframe thead tr th {
        background: #F1F5F9 !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.5rem 0.75rem !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        overflow: hidden;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #E2E8F0;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        color: #64748B;
    }

    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom: 2px solid #2563EB !important;
    }

    .sidebar-footer {
        position: fixed;
        bottom: 1rem;
        color: #475569;
        font-size: 0.7rem;
    }

    .stButton button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.4rem 1rem !important;
        font-size: 0.85rem !important;
        transition: all 0.2s;
    }

    .stButton button[kind="primary"] {
        background: #2563EB !important;
        color: white !important;
        border: none !important;
    }

    .stButton button[kind="primary"]:hover {
        background: #1D4ED8 !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    div[data-testid="stMetric"] label {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B !important;
    }

    div[data-testid="stMetric"] div {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    hr {
        border-color: #E2E8F0 !important;
    }

    .call-message {
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .call-message.ai {
        background: #EFF6FF;
        border-left: 3px solid #2563EB;
        color: #1E40AF;
    }

    .call-message.customer {
        background: #F9FAFB;
        border-left: 3px solid #10B981;
        color: #065F46;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.authenticated:
    from pages import login
    login.show()
    st.stop()

from pages import dashboard, leads, campaigns, call_history, settings

with st.sidebar:
    st.markdown('<div class="sidebar-title">📞 AI Cold Calling</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Production v2.0</div>', unsafe_allow_html=True)
    st.markdown("---")

    user = st.session_state.get("user", {})
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0.5rem;padding:0.25rem 0 0.75rem 0;">'
        f'<div style="width:32px;height:32px;border-radius:50%;background:#2563EB;'
        f'display:flex;align-items:center;justify-content:center;color:white;font-weight:600;font-size:0.85rem;">'
        f'{user.get("full_name","U")[0].upper()}</div>'
        f'<div><div style="color:white;font-size:0.85rem;font-weight:500;">{user.get("full_name","User")}</div>'
        f'<div style="color:#94A3B8;font-size:0.7rem;">{user.get("role","agent").title()}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Dashboard", "Leads", "Campaigns", "Call History", "Settings"],
        label_visibility="collapsed",
        index=0,
    )

    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("🟢")
    with col2:
        st.markdown('<span style="color:#94A3B8;font-size:0.75rem;">System Online</span>', unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None
        st.rerun()

    st.markdown(
        f'<div style="color:#475569;font-size:0.7rem;margin-top:0.5rem;">v2.0.0 Production<br>{datetime.now().strftime("%b %d, %Y")}</div>',
        unsafe_allow_html=True,
    )

if page == "Dashboard":
    dashboard.show()
elif page == "Leads":
    leads.show()
elif page == "Campaigns":
    campaigns.show()
elif page == "Call History":
    call_history.show()
elif page == "Settings":
    settings.show()
