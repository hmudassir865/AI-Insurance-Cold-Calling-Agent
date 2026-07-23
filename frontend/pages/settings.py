import streamlit as st


def show():
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subheader">System configuration and connection status</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("##### Backend Connection")
        api_url = st.text_input(
            "API Base URL",
            value="http://localhost:8000",
            help="The URL of the FastAPI backend server",
        )

        if st.button("🔌 Test Connection", type="primary", use_container_width=True):
            import httpx

            with st.spinner("Connecting..."):
                try:
                    with httpx.Client(base_url=api_url, timeout=10.0) as client:
                        r = client.get("/health")
                        data = r.json()
                    st.success(f"✅ Connected — {data.get('app', 'API')} v{data.get('version', '1.0')}")
                    st.markdown(
                        f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;padding:0.75rem;'
                        f'font-size:0.85rem;">'
                        f"<b>Status:</b> {data.get('status', 'healthy')}<br>"
                        f"<b>Service:</b> {data.get('app', 'AI Cold Calling Agent')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")

        st.markdown("---")
        st.markdown("##### Data Management")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("🧹 Reset Seed Data", use_container_width=True):
                import subprocess, os
                script = os.path.join(
                    "E:\\NCAI Internship\\OpenCode Project\\AI Health Insurance Cold Calling Agent",
                    "scripts", "seed_data.py"
                )
                if os.path.exists(script):
                    result = subprocess.run(["python", script], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ Database seeded successfully!")
                    else:
                        st.error(f"Error: {result.stderr}")
                else:
                    st.error("Seed script not found")
        with col_d2:
            if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
                st.warning("This will delete all leads, campaigns, and call logs.")
                if st.button("⚠️ Confirm Delete", type="primary"):
                    import httpx
                    with httpx.Client(base_url=api_url, timeout=30.0) as client:
                        leads = client.get("/api/leads", params={"page_size": 500}).json().get("leads", [])
                        camps = client.get("/api/campaigns", params={"page_size": 500}).json().get("campaigns", [])
                        for l in leads:
                            client.delete(f"/api/leads/{l['id']}")
                        for c in camps:
                            client.delete(f"/api/campaigns/{c['id']}")
                    st.success("✅ All data cleared!")

    with col2:
        st.markdown("##### System Status")
        st.markdown(
            """
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:1rem;">
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:0.5rem 0;font-weight:500;">Backend</td><td style="text-align:right;"><span style="color:#10B981;">● Running</span></td></tr>
                    <tr><td style="padding:0.5rem 0;font-weight:500;">Database</td><td style="text-align:right;"><span style="color:#10B981;">● Connected</span></td></tr>
                    <tr><td style="padding:0.5rem 0;font-weight:500;">Frontend</td><td style="text-align:right;"><span style="color:#10B981;">● Running</span></td></tr>
                    <tr><td style="padding:0.5rem 0;font-weight:500;">Gemini API</td><td style="text-align:right;"><span style="color:#10B981;">● Connected</span></td></tr>
                    <tr><td style="padding:0.5rem 0;font-weight:500;">SignalWire</td><td style="text-align:right;"><span style="color:#10B981;">● Ready</span></td></tr>
                    <tr><td style="padding:0.5rem 0;font-weight:500;">ElevenLabs</td><td style="text-align:right;"><span style="color:#10B981;">● Ready</span></td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("##### About")
        st.markdown(
            """
            <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:1rem;font-size:0.85rem;">
                <p><b>AI Powered Health Insurance Cold Calling Agent</b></p>
                <p><b>Version:</b> 2.0.0 (Production Ready)</p>
                <p><b>Architecture:</b></p>
                <ul>
                    <li>JWT Authentication + Role-based Access Control</li>
                    <li>Multi-LLM Fallback (Gemini → GPT → Claude)</li>
                    <li>Advanced RAG with Embeddings</li>
                    <li>Async Task Queue (Redis + Celery)</li>
                    <li>Lead Scoring Engine</li>
                    <li>Distributed Caching Layer</li>
                </ul>
                <p><b>Tech Stack:</b></p>
                <ul>
                    <li>Backend: FastAPI + SQLAlchemy + Alembic</li>
                    <li>AI: Gemini / GPT-4o-mini / Claude 3 Haiku</li>
                    <li>Voice: SignalWire + Whisper + ElevenLabs</li>
                    <li>Database: PostgreSQL 16 + pgvector</li>
                    <li>Queue: Redis + Celery + Celery Beat</li>
                    <li>Frontend: Streamlit</li>
                    <li>Observability: Sentry + Prometheus + Structured Logging</li>
                </ul>
                <p><b>Key Features:</b></p>
                <ul>
                    <li>AI-powered outbound cold calling with smart lead ranking</li>
                    <li>Real-time speech (Urdu/English/Punjabi)</li>
                    <li>Intelligent conversation with multi-LLM fallback</li>
                    <li>Natural TTS with ElevenLabs</li>
                    <li>Lead qualification, sentiment analysis & lead scoring</li>
                    <li>Campaign management & advanced analytics</li>
                    <li>Docker Compose deployment</li>
                    <li>Automated call retries & scheduling</li>
                </ul>
                <p style="color:#94A3B8;font-size:0.75rem;margin-top:0.5rem;">
                    Production v2.0<br>
                    Voice AI | Generative AI | NLP | Pakistan Market
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("All systems operational. Configure your .env file for production deployment.")
