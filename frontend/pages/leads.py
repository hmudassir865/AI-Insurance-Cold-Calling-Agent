import streamlit as st
import pandas as pd

from utils.api_client import (
    list_leads,
    create_lead,
    bulk_upload_leads,
    update_lead,
    delete_lead,
    list_campaigns,
    initiate_call,
)


def _badge(status: str) -> str:
    cls = status.lower().replace(" ", "_")
    return f'<span class="status-badge {cls}">{status.replace("_", " ").title()}</span>'


def show():
    st.markdown('<div class="main-header">Leads Management</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subheader">Upload, manage, and track your customer leads</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📋 All Leads", "➕ Add Lead", "📤 Bulk Upload"])

    with tab1:
        col_f1, col_f2, col_f3, col_f4 = st.columns([1.5, 1.5, 1.5, 1])
        with col_f1:
            status_filter = st.selectbox(
                "Status",
                ["All", "pending", "called", "interested", "not_interested", "callback", "busy", "wrong_number"],
                key="lead_status_filter",
            )
        with col_f2:
            search = st.text_input("Search", placeholder="Name or phone...", key="lead_search")
        with col_f3:
            campaigns_resp = list_campaigns()
            camp_opts = {c["name"]: c["id"] for c in campaigns_resp.get("campaigns", [])}
            camp_opts["All Campaigns"] = None
            sel_camp = st.selectbox("Campaign", list(camp_opts.keys()), key="lead_camp_filter")
        with col_f4:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("🔄 Refresh", key="refresh_leads", use_container_width=True)

        params = {"page": 1, "page_size": 200}
        if status_filter != "All":
            params["status"] = status_filter
        if search:
            params["search"] = search
        if sel_camp != "All Campaigns":
            params["campaign_id"] = camp_opts[sel_camp]

        with st.spinner("Loading leads..."):
            data = list_leads(**params)

        leads = data.get("leads", [])
        total = data.get("total", 0)

        col_info, col_action = st.columns([3, 1])
        with col_info:
            st.markdown(f'<span style="font-size:0.9rem;color:#475569;">Showing <b>{len(leads)}</b> of <b>{total}</b> leads</span>', unsafe_allow_html=True)
        with col_action:
            if st.button("🗑️ Clear All Leads", type="secondary", use_container_width=True, disabled=total == 0):
                for l in leads:
                    delete_lead(l["id"])
                st.rerun()

        if leads:
            for idx, l in enumerate(leads):
                with st.container():
                    header_cols = st.columns([3, 1.5, 1, 1])
                    with header_cols[0]:
                        st.markdown(
                            f'<span style="font-weight:600;font-size:1rem;">{l["name"]}</span>'
                            f'<br><span style="font-size:0.8rem;color:#64748B;">{l["phone"]}</span>',
                            unsafe_allow_html=True,
                        )
                    with header_cols[1]:
                        st.markdown(
                            f'<span style="font-size:0.85rem;">{l["language"].upper()}</span>',
                            unsafe_allow_html=True,
                        )
                    with header_cols[2]:
                        st.markdown(_badge(l["status"]), unsafe_allow_html=True)
                    with header_cols[3]:
                        st.markdown(
                            f'<span style="font-size:0.75rem;color:#94A3B8;">{l["created_at"][:10]}</span>',
                            unsafe_allow_html=True,
                        )

                    with st.expander("⚡ Actions & Details", expanded=False):
                        det_cols = st.columns(5)
                        det_cols[0].metric("Status", l["status"].replace("_", " ").title())
                        det_cols[1].metric("Language", l["language"].upper())
                        det_cols[2].metric("Campaign", str(l.get("assigned_campaign_id", "N/A")[:8] + "...") if l.get("assigned_campaign_id") else "None")
                        det_cols[3].metric("Created", l["created_at"][:10])
                        det_cols[4].metric("Lead ID", l["id"][:8] + "...")

                        a1, a2, a3, a4, a5 = st.columns([1.2, 1.2, 1.2, 1.2, 1])
                        with a1:
                            new_st = st.selectbox(
                                "New status",
                                ["pending", "interested", "not_interested", "callback", "busy", "wrong_number"],
                                key=f"st_{l['id']}",
                                label_visibility="collapsed",
                            )
                        with a2:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("✅ Update", key=f"upd_{l['id']}", use_container_width=True):
                                update_lead(l["id"], {"status": new_st})
                                st.success("Updated!")
                                st.rerun()
                        with a3:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("📞 Call", key=f"call_{l['id']}", use_container_width=True):
                                try:
                                    result = initiate_call(l["id"])
                                    st.info(f"Calling {l['name']}...")
                                except Exception as e:
                                    st.error(f"Call failed: {e}")
                        with a4:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("🗑️ Delete", key=f"del_{l['id']}", use_container_width=True, type="primary"):
                                delete_lead(l["id"])
                                st.rerun()
                        with a5:
                            if l.get("extra_data") and isinstance(l["extra_data"], dict):
                                st.markdown("<br>", unsafe_allow_html=True)
                                with st.popover("📋 Extra", use_container_width=True):
                                    st.json(l["extra_data"])

                    st.markdown("---")
        else:
            st.info("No leads found. Upload a CSV or add a lead manually.")

    with tab2:
        st.markdown("##### Add Single Lead")
        with st.form("add_lead_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", placeholder="e.g., Ahmed Khan")
            with col2:
                phone = st.text_input(
                    "Phone Number", placeholder="e.g., +923001234567"
                )

            language = st.selectbox(
                "Preferred Language",
                ["urdu", "english", "punjabi"],
                help="The AI will speak in this language",
            )

            submitted = st.form_submit_button("➕ Add Lead", type="primary", use_container_width=True)

            if submitted:
                if not name or not phone:
                    st.error("Name and phone are required")
                else:
                    with st.spinner("Creating lead..."):
                        try:
                            result = create_lead(name, phone, language)
                            st.success(f"✅ Lead '{result['name']}' created successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")

    with tab3:
        st.markdown("##### Bulk Upload Leads (CSV)")
        st.info(
            "📄 **CSV Format:** `name, phone, language` (language is optional, defaults to Urdu)"
        )
        with st.expander("📝 Show Example CSV Format"):
            st.code(
                "name,phone,language\n"
                "Ahmed Khan,+923001234567,urdu\n"
                "Fatima Ali,+923001234568,english\n"
                "Muhammad Usman,+923001234569,punjabi",
                language="text",
            )

        uploaded_file = st.file_uploader(
            "Choose a CSV file to upload", type="csv"
        )

        if uploaded_file is not None:
            preview_df = pd.read_csv(uploaded_file)
            st.markdown("##### Preview")
            st.dataframe(preview_df.head(5), use_container_width=True, hide_index=True)
            st.caption(f"Total rows: {len(preview_df)}")

            campaigns_resp = list_campaigns()
            camp_opts = {c["name"]: c["id"] for c in campaigns_resp.get("campaigns", [])}
            camp_opts["None"] = None
            sel_camp_name = st.selectbox("Assign to campaign", list(camp_opts.keys()), key="bulk_camp")
            sel_camp_id = camp_opts[sel_camp_name]

            if st.button("📤 Upload Leads", type="primary", use_container_width=True):
                with st.spinner("Uploading..."):
                    try:
                        result = bulk_upload_leads(
                            uploaded_file.getvalue(), uploaded_file.name, campaign_id=sel_camp_id
                        )
                        st.success(f"✅ Uploaded {result['total_uploaded']} leads!")
                        if result.get("errors"):
                            st.warning(
                                f"⚠️ {len(result['errors'])} errors: "
                                + "; ".join(result["errors"][:5])
                            )
                    except Exception as e:
                        st.error(f"Upload failed: {e}")
