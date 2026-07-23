import streamlit as st
import pandas as pd

from utils.api_client import get_call_history


def show():
    st.markdown('<div class="main-header">Call History</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subheader">Review all AI-powered calls with transcripts and insights</div>',
        unsafe_allow_html=True,
    )

    col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 1])
    with col_f1:
        status_filter = st.selectbox(
            "Status",
            ["All", "completed", "failed", "no-answer", "busy", "initiated"],
            key="call_status_filter",
        )
    with col_f2:
        search_lead = st.text_input("Search by Lead ID", placeholder="Paste lead ID...")
    with col_f3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔄 Refresh", key="refresh_calls", use_container_width=True)

    params = {"page": 1, "page_size": 100}
    if status_filter != "All":
        params["status"] = status_filter
    if search_lead:
        params["lead_id"] = search_lead

    with st.spinner("Loading call history..."):
        try:
            data = get_call_history(**params)
        except Exception as e:
            st.error(f"Failed to load call history: {e}")
            return

    call_logs = data.get("call_logs", [])
    total = data.get("total", 0)

    st.markdown(
        f'<span style="font-size:0.9rem;color:#475569;">Showing <b>{len(call_logs)}</b> of <b>{total}</b> calls</span>',
        unsafe_allow_html=True,
    )

    if not call_logs:
        st.info("No call history yet. Start a campaign to see calls here.")
        return

    for call in call_logs:
        with st.container():
            cols = st.columns([1.5, 1.5, 1, 1, 0.5])
            with cols[0]:
                dur = call.get("duration_seconds")
                dur_str = f"{dur}s" if dur else "—"
                st.markdown(
                    f'<span style="font-weight:600;font-size:0.9rem;">{call.get("created_at","")[:19]}</span>',
                    unsafe_allow_html=True,
                )
            with cols[1]:
                sid = call.get("lead_id", "")
                st.markdown(
                    f'<span style="font-size:0.8rem;color:#64748B;">Lead: {sid[:8]}...</span>',
                    unsafe_allow_html=True,
                )
            with cols[2]:
                st.markdown(dur_str)
            with cols[3]:
                st.markdown(
                    f'<span class="status-badge {call.get("status","")}">{call.get("status","")}</span>',
                    unsafe_allow_html=True,
                )
            with cols[4]:
                sent = call.get("sentiment_score")
                sent_str = f"{sent:.2f}" if sent is not None else "—"
                st.markdown(
                    f'<span style="font-weight:600;font-size:0.9rem;">{sent_str}</span>',
                    unsafe_allow_html=True,
                )

            with st.expander("📄 View Details", expanded=False):
                det_cols = st.columns(4)
                det_cols[0].metric("Duration", f"{call.get('duration_seconds','N/A')}s")
                det_cols[1].metric("Sentiment", f"{call.get('sentiment_score','N/A')}")
                det_cols[2].metric("Lead Status", call.get("lead_status", "N/A").replace("_", " ").title() if call.get("lead_status") else "N/A")
                det_cols[3].metric("Call Status", call.get("status", "N/A").title())

                if call.get("summary"):
                    st.markdown("###### AI Summary")
                    st.info(call["summary"])

                if call.get("transcript"):
                    st.markdown("###### Conversation Transcript")
                    transcript = call["transcript"]
                    if isinstance(transcript, list):
                        for entry in transcript:
                            role = entry.get("role", "")
                            content = entry.get("content", "")
                            cls = "ai" if role == "assistant" else "customer"
                            label = "🤖 AI" if role == "assistant" else "👤 Customer"
                            st.markdown(
                                f'<div class="call-message {cls}">'
                                f'<strong>{label}</strong><br>{content}'
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.text(str(transcript))

                if call.get("error_message"):
                    st.error(f"Error: {call['error_message']}")

            st.markdown("---")
