import streamlit as st
import pandas as pd

from utils.api_client import (
    list_campaigns,
    get_campaign_analytics,
    create_campaign,
    start_campaign,
    pause_campaign,
    delete_campaign,
    list_leads,
    initiate_call,
)


DEFAULT_SCRIPT = """Assalam-o-Alaikum! Main [Company Name] se health insurance ke baare mein baat kar raha hoon.

Aap ko sahi se health insurance plan chuna hai jo aap ki zarooraton ko poora kare. Hum basic hospitalization se lekar comprehensive family plans tak mukhtalif options provide karte hain.

Kya main aap ko hamare plans ke baare mein thodi aur wazahat de sakta hoon? [Listen]

[If interested]: Humein 500+ hospitals mein cashless facility hai. Plans sirf PKR 2,000/month se shuru hote hain.

[If price concern]: Aap ko long-term mein yeh plan bohot afford lagay ga, kyunki ek accident ya hospitalization se lakhon rupees ka kharcha aa sakta hai.

[If not interested]: Koi baat nahi, agar aap ko future mein zaroorat ho to hum dobara contact kar sakte hain.

Shukriya aap ke waqt ke liye! Allah Hafiz."""

DEFAULT_GREETING = "Assalam-o-Alaikum! Main [Company Name] se health insurance ke baare mein baat kar raha hoon. Kya main aap se kuch baat kar sakta hoon?"
DEFAULT_CLOSING = "Shukriya aap ke waqt ke liye! Allah Hafiz."


def _badge(status: str) -> str:
    cls = status.lower()
    return f'<span class="status-badge {cls}">{status.title()}</span>'


def show():
    st.markdown('<div class="main-header">Campaigns</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subheader">Create and manage your AI cold calling campaigns</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📢 Campaigns", "➕ New Campaign"])

    with tab1:
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "draft", "active", "paused", "completed"],
                key="camp_status_filter",
            )
        with col_f2:
            st.button("🔄 Refresh", key="refresh_camps", use_container_width=True)

        with st.spinner("Loading campaigns..."):
            if status_filter != "All":
                data = list_campaigns(status=status_filter, page=1, page_size=50)
            else:
                data = get_campaign_analytics()

        campaigns = data.get("campaigns", [])

        if not campaigns:
            st.info("No campaigns found. Create one in the 'New Campaign' tab.")
        else:
            for camp in campaigns:
                with st.container():
                    cols = st.columns([3, 1, 1, 1, 0.5])
                    with cols[0]:
                        st.markdown(
                            f'<span style="font-weight:600;font-size:1rem;">{camp["name"]}</span>'
                            f" {_badge(camp['status'])}",
                            unsafe_allow_html=True,
                        )
                    with cols[1]:
                        st.metric("Leads", f"{camp['processed_leads']}/{camp['total_leads']}")
                    with cols[2]:
                        st.metric("Calls", camp.get("total_calls", 0))
                    with cols[3]:
                        st.metric("Conv.", f"{camp.get('conversion_rate', 0):.1f}%")
                    with cols[4]:
                        st.metric("Sent.", f"{camp.get('avg_sentiment', 0):.2f}")

                    act_cols = st.columns(6)
                    with act_cols[0]:
                        if camp["status"] == "draft":
                            if st.button("▶️ Start", key=f"start_{camp['id']}"):
                                result = start_campaign(camp["id"])
                                st.success(result["message"])
                                st.rerun()
                    with act_cols[1]:
                        if camp["status"] == "active":
                            if st.button("⏸️ Pause", key=f"pause_{camp['id']}"):
                                pause_campaign(camp["id"])
                                st.success("Paused")
                                st.rerun()
                    with act_cols[2]:
                        if st.button("📞 Test Call", key=f"call_{camp['id']}"):
                            leads_data = list_leads(campaign_id=camp["id"], status="pending", page=1, page_size=1)
                            pending = leads_data.get("leads", [])
                            if pending:
                                try:
                                    r = initiate_call(pending[0]["id"], camp["id"])
                                    st.info(f"Calling {pending[0]['name']}...")
                                except Exception as e:
                                    st.error(f"Call failed: {e}")
                            else:
                                st.warning("No pending leads")
                    with act_cols[3]:
                        status_opts = ["draft", "active", "paused", "completed"]
                        new_st = st.selectbox(
                            "Status", status_opts,
                            index=status_opts.index(camp["status"]),
                            key=f"st_{camp['id']}",
                            label_visibility="collapsed",
                        )
                    with act_cols[4]:
                        if new_st != camp["status"]:
                            from utils.api_client import update_campaign
                            update_campaign(camp["id"], {"status": new_st})
                            st.rerun()

                    with act_cols[5]:
                        if st.button("🗑️", key=f"del_{camp['id']}"):
                            delete_campaign(camp["id"])
                            st.rerun()

                    st.markdown("**Script:**")
                    st.code(camp.get("script_template", "No script")[:300] + "...", language="text")
                    st.markdown("---")

    with tab2:
        st.markdown("##### Create New Campaign")
        with st.form("create_campaign_form", clear_on_submit=True):
            name = st.text_input(
                "Campaign Name",
                placeholder="e.g., Health Insurance Q4 Outreach",
            )

            greeting = st.text_input("Greeting Message", value=DEFAULT_GREETING)
            closing = st.text_input("Closing Message", value=DEFAULT_CLOSING)

            script_template = st.text_area(
                "Call Script Template",
                value=DEFAULT_SCRIPT,
                height=250,
                help="The AI will use this script as a guide during calls.",
            )

            submitted = st.form_submit_button("🚀 Create Campaign", type="primary", use_container_width=True)

            if submitted:
                if not name:
                    st.error("Campaign name is required")
                else:
                    with st.spinner("Creating campaign..."):
                        try:
                            result = create_campaign(name, script_template, greeting, closing)
                            st.success(f"✅ Campaign '{result['name']}' created!")
                        except Exception as e:
                            st.error(f"Error: {e}")
