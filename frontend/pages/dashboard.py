import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.api_client import get_dashboard


def _status_badge(status: str) -> str:
    badges = {
        "pending": "pending", "interested": "interested",
        "not_interested": "not_interested", "callback": "callback",
        "busy": "busy", "completed": "completed", "active": "active",
        "draft": "draft", "paused": "paused", "failed": "failed",
    }
    cls = badges.get(status.lower(), "pending")
    return f'<span class="status-badge {cls}">{status.replace("_", " ").title()}</span>'


def show():
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subheader">Real-time overview of your cold calling campaigns</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        days = st.selectbox("Time Range", [7, 14, 30, 90], index=0)
    with col3:
        st.button("🔄 Refresh", type="secondary", use_container_width=True)

    with st.spinner("Loading dashboard data..."):
        data = get_dashboard(days=days)

    if "detail" in data:
        st.error(f"Backend error: {data['detail']}")
        return

    st.markdown("##### Key Metrics")
    metrics = [
        ("📞", "Total Calls", str(data.get("total_calls", 0))),
        ("👤", "Total Leads", str(data.get("total_leads", 0))),
        ("🎯", "Conversion Rate", f"{data.get('conversion_rate', 0):.1f}%"),
        ("⏱️", "Avg Duration", f"{data.get('avg_call_duration_seconds', 0):.0f}s"),
        ("😊", "Avg Sentiment", f"{data.get('avg_sentiment_score', 0):.2f}"),
    ]
    cols = st.columns(5)
    for col, (icon, label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-icon">{icon}</div>'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-label">{label}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    lead_bd = data.get("lead_breakdown", {})
    daily_stats = data.get("daily_stats", [])

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("##### Lead Status Breakdown")
        if lead_bd:
            df = pd.DataFrame(
                {
                    "Status": [
                        s.replace("_", " ").title() for s in lead_bd.keys()
                    ],
                    "Count": list(lead_bd.values()),
                }
            ).sort_values("Count", ascending=False)
            st.bar_chart(df.set_index("Status"), height=250, use_container_width=True)

            total_leads = sum(lead_bd.values())
            if total_leads > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                for status, count in sorted(
                    lead_bd.items(), key=lambda x: x[1], reverse=True
                ):
                    pct = (count / total_leads) * 100
                    bar_color = {
                        "interested": "#10B981",
                        "not_interested": "#EF4444",
                        "callback": "#3B82F6",
                        "pending": "#F59E0B",
                        "busy": "#8B5CF6",
                        "wrong_number": "#6B7280",
                        "dnc": "#6B7280",
                        "called": "#6366F1",
                    }.get(status, "#CBD5E1")
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.35rem;">'
                        f'<span style="font-size:0.8rem;font-weight:500;color:#475569;min-width:7rem;">{status.replace("_"," ").title()}</span>'
                        f'<div style="flex:1;height:1.25rem;background:#F1F5F9;border-radius:6px;overflow:hidden;">'
                        f'<div style="height:100%;width:{pct}%;background:{bar_color};border-radius:6px;transition:width 0.5s;"></div>'
                        f"</div>"
                        f'<span style="font-size:0.8rem;font-weight:600;color:#0F172A;min-width:3rem;text-align:right;">{count}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    with col_right:
        st.markdown("##### Daily Call Activity")
        if daily_stats:
            df_daily = pd.DataFrame(daily_stats)
            df_daily["date"] = pd.to_datetime(df_daily["date"])
            df_daily = df_daily.sort_values("date")

            st.line_chart(
                df_daily.set_index("date")["calls"],
                height=150,
                use_container_width=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(
                    "Avg Duration Today",
                    f"{df_daily.iloc[-1]['avg_duration']:.0f}s"
                    if not df_daily.empty
                    else "—",
                )
            with col_b:
                st.metric(
                    "Avg Sentiment Today",
                    f"{df_daily.iloc[-1]['avg_sentiment']:.2f}"
                    if not df_daily.empty
                    else "—",
                )
        else:
            st.info("No call activity yet. Start a campaign to see data here.")

    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh every 60s")
