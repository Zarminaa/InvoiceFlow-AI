"""InvoiceFlow AI — Enterprise Review & Verification Console.

A minimalist, high-density interface inspired by Linear and Stripe.
OCR-grounded KIE · Human-in-the-Loop Review · Four-Eyes Governance · Idempotent RPA Handoff.
Zero emojis, clean typography, tabular figures, and real-time arithmetic auditing.
"""
from __future__ import annotations

import io
import os
import time
from typing import Any

import httpx
import pandas as pd
import streamlit as st

from invoiceflow_ai.evidence import render_overlay
from frontend.sample_data import (
    generate_clean_medicine_sample,
    generate_dropped_row_sample,
    generate_payment_sample,
)

# -----------------------------------------------------------------------------
# Page Configuration & Minimalist Modern Enterprise Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="InvoiceFlow AI — Review Console",
    layout="wide",
    initial_sidebar_state="expanded",
)

MINIMALIST_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        letter-spacing: -0.011em;
    }

    code, pre, .stCode, .font-mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Clean Header Bar */
    .top-header {
        border-bottom: 1px solid #27272a;
        padding-bottom: 16px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .brand-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f4f4f5;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .brand-badge {
        font-size: 0.65rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
        background: #18181b;
        color: #a1a1aa;
        border: 1px solid #27272a;
        text-transform: uppercase;
    }

    /* Minimal Metric KPI Cards */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }

    .kpi-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 12px 14px;
    }

    .kpi-title {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #71717a;
        margin-bottom: 4px;
    }

    .kpi-num {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f4f4f5;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }

    /* Status Pills */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }

    .badge-approved {
        background: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .badge-reviewed {
        background: rgba(37, 99, 235, 0.1);
        color: #60a5fa;
        border: 1px solid rgba(37, 99, 235, 0.25);
    }

    .badge-pending {
        background: rgba(245, 158, 11, 0.1);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }

    .badge-blocked {
        background: rgba(244, 63, 94, 0.1);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.25);
    }

    /* Arithmetic verification banner */
    .banner-match {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 6px;
        padding: 10px 14px;
        color: #34d399;
        font-size: 0.8rem;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .banner-mismatch {
        background: rgba(244, 63, 94, 0.08);
        border: 1px solid rgba(244, 63, 94, 0.25);
        border-radius: 6px;
        padding: 10px 14px;
        color: #fb7185;
        font-size: 0.8rem;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Clean Card Container */
    .card-panel {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }

    /* Subdued Buttons */
    button[kind="primary"] {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        border-radius: 6px !important;
    }
    button[kind="secondary"] {
        background-color: #18181b !important;
        border-color: #27272a !important;
        color: #d4d4d8 !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        border-radius: 6px !important;
    }

    /* Clean Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0c0c0e !important;
        border-right: 1px solid #27272a !important;
    }
</style>
"""
st.markdown(MINIMALIST_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Connection & Environment State
# -----------------------------------------------------------------------------
DEFAULT_API_URL = "http://127.0.0.1:8000"
DEFAULT_DEMO_KEY = "local-demo-operator-key-default-16chars"

if "api_url" not in st.session_state:
    st.session_state["api_url"] = os.getenv("INVOICEFLOW_API_URL", DEFAULT_API_URL).rstrip("/")
if "api_key" not in st.session_state:
    st.session_state["api_key"] = os.getenv("INVOICEFLOW_API_KEY", DEFAULT_DEMO_KEY)
if "approver_key" not in st.session_state:
    st.session_state["approver_key"] = os.getenv("INVOICEFLOW_APPROVER_API_KEY", "")
if "selected_document" not in st.session_state:
    st.session_state["selected_document"] = ""

api_url = st.session_state["api_url"]
api_key = st.session_state["api_key"]
approver_key = st.session_state["approver_key"]


# -----------------------------------------------------------------------------
# HTTP Communication Client
# -----------------------------------------------------------------------------
def api_request(method: str, path: str, *, key: str | None = None, **kwargs) -> httpx.Response | None:
    use_key = key if key is not None else api_key
    headers = {"X-API-Key": use_key}
    try:
        with httpx.Client(base_url=api_url, timeout=30.0) as client:
            resp = client.request(method, path, headers=headers, **kwargs)
            if resp.status_code >= 400:
                st.error(f"API Error ({resp.status_code}): {resp.text[:300]}")
                return None
            return resp
    except httpx.ConnectError:
        st.error(f"Connection failed: unable to reach {api_url}")
        return None
    except Exception as exc:
        st.error(f"Request failed: {type(exc).__name__}: {exc}")
        return None


def fetch_all_documents() -> list[dict[str, Any]]:
    resp = api_request("GET", "/api/v1/documents?limit=100")
    return resp.json() if resp is not None else []


# -----------------------------------------------------------------------------
# Sidebar: Control Center
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f4f4f5; margin-bottom: 8px;'>INVOICEFLOW</div>", unsafe_allow_html=True)
    
    # Latency Probe
    def check_health() -> tuple[bool, float]:
        try:
            t0 = time.perf_counter()
            with httpx.Client(base_url=api_url, timeout=3.0) as client:
                r = client.get("/health")
                ms = (time.perf_counter() - t0) * 1000
                if r.status_code == 200:
                    return True, ms
        except Exception:
            pass
        return False, 0.0

    is_online, ping_ms = check_health()
    if is_online:
        st.markdown(
            f"""
            <div style="background: #18181b; border: 1px solid #27272a; border-radius: 6px; padding: 8px 12px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.75rem; font-weight: 600; color: #34d399;">API Online</span>
                    <span style="font-size: 0.7rem; font-family: monospace; color: #71717a;">{ping_ms:.0f}ms</span>
                </div>
                <div style="font-size: 0.7rem; color: #71717a; margin-top: 2px; font-family: monospace;">{api_url}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background: #18181b; border: 1px solid #27272a; border-radius: 6px; padding: 8px 12px; margin-bottom: 16px;">
                <span style="font-size: 0.75rem; font-weight: 600; color: #fb7185;">API Offline</span>
                <div style="font-size: 0.7rem; color: #71717a; margin-top: 2px;">Start backend: invoiceflow api</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Navigation Tabs
    active_nav = st.radio(
        "Navigation",
        [
            "Workspace & Review",
            "Document Queue",
            "Four-Eyes Approval",
            "ERP Simulator",
            "Audit Ledger",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    with st.expander("Connection Settings", expanded=False):
        api_url_input = st.text_input("API URL", value=st.session_state["api_url"])
        api_key_input = st.text_input("Operator Key", value=st.session_state["api_key"], type="password")
        approver_key_input = st.text_input("Approver Key (Rule R-302)", value=st.session_state["approver_key"], type="password")
        if st.button("Save", use_container_width=True):
            st.session_state["api_url"] = api_url_input.rstrip("/")
            st.session_state["api_key"] = api_key_input
            st.session_state["approver_key"] = approver_key_input
            st.rerun()


# -----------------------------------------------------------------------------
# Top Global Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="top-header">
        <div class="brand-title">
            <span>InvoiceFlow</span>
            <span class="brand-badge">Verification Console</span>
        </div>
        <div style="font-size: 0.75rem; color: #71717a;">
            Vietnamese Medical KIE · OCR Grounding · Four-Eyes Governance
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch current state metrics
all_docs = fetch_all_documents() if is_online else []
total_docs = len(all_docs)
pending_docs = sum(1 for d in all_docs if d["status"] in ("PENDING_REVIEW", "BLOCKED_VALIDATION"))
reviewed_docs = sum(1 for d in all_docs if d["status"] == "REVIEWED")
approved_docs = sum(1 for d in all_docs if d["status"] == "APPROVED")

# Render Minimal Metric Cards
st.markdown(
    f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-title">Total Ingested</div>
            <div class="kpi-num">{total_docs}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Needs Review</div>
            <div class="kpi-num" style="color: #fbbf24;">{pending_docs}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Human-Verified</div>
            <div class="kpi-num" style="color: #60a5fa;">{reviewed_docs}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Approved & Released</div>
            <div class="kpi-num" style="color: #34d399;">{approved_docs}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# TAB 1: WORKSPACE & REVIEW
# -----------------------------------------------------------------------------
if active_nav == "Workspace & Review":
    
    # Document Selection Bar & Demo Launchpad
    col_sel, col_demo = st.columns([1.8, 1.2], gap="medium")
    
    with col_sel:
        doc_options = [d["id"] for d in all_docs]
        if doc_options:
            cur_idx = doc_options.index(st.session_state["selected_document"]) if st.session_state["selected_document"] in doc_options else 0
            picked_doc = st.selectbox("Active Document", doc_options, index=cur_idx, format_func=lambda x: f"{x[:14]}... ({next((d['status'] for d in all_docs if d['id'] == x), '')})")
            st.session_state["selected_document"] = picked_doc
        else:
            st.text_input("Active Document ID", value="", placeholder="Queue empty; load demo below", disabled=True)

    with col_demo:
        st.markdown("<div style='font-size:0.75rem; font-weight:600; color:#a1a1aa; margin-bottom:4px;'>Load Synthetic Scenario</div>", unsafe_allow_html=True)
        cd1, cd2, cd3 = st.columns(3)
        with cd1:
            if st.button("Clean", help="3 medicine items, balanced arithmetic", use_container_width=True):
                img_b, res_d = generate_clean_medicine_sample()
                imp = api_request("POST", "/api/v1/documents/import", json={"result": res_d, "source": "clean_scenario"})
                if imp:
                    did = imp.json()["id"]
                    api_request("PUT", f"/api/v1/documents/{did}/image", files={"file": ("sample.png", img_b, "image/png")})
                    st.session_state["selected_document"] = did
                    st.rerun()
        with cd2:
            if st.button("Mismatch", help="Dropped row 3, flags discrepancy", use_container_width=True):
                img_b, res_d = generate_dropped_row_sample()
                imp = api_request("POST", "/api/v1/documents/import", json={"result": res_d, "source": "mismatch_scenario"})
                if imp:
                    did = imp.json()["id"]
                    api_request("PUT", f"/api/v1/documents/{did}/image", files={"file": ("sample.png", img_b, "image/png")})
                    st.session_state["selected_document"] = did
                    st.rerun()
        with cd3:
            if st.button("Payment", help="Hospital BHYT insurance split", use_container_width=True):
                img_b, res_d = generate_payment_sample()
                imp = api_request("POST", "/api/v1/documents/import", json={"result": res_d, "source": "payment_scenario"})
                if imp:
                    did = imp.json()["id"]
                    api_request("PUT", f"/api/v1/documents/{did}/image", files={"file": ("sample.png", img_b, "image/png")})
                    st.session_state["selected_document"] = did
                    st.rerun()

    active_id = st.session_state.get("selected_document", "")
    if not active_id:
        st.info("No document selected. Click one of the scenario buttons above to load a demonstration.")
        st.stop()

    doc_resp = api_request("GET", f"/api/v1/documents/{active_id}")
    if not doc_resp:
        st.stop()
    
    doc = doc_resp.json()
    status = doc["status"]
    doc_type = doc.get("reviewed_document_type") or doc.get("original_document_type", "UNKNOWN")

    # Document Header Ribbon
    status_cls = (
        "badge-approved" if status == "APPROVED"
        else "badge-reviewed" if status == "REVIEWED"
        else "badge-blocked" if "BLOCKED" in status
        else "badge-pending"
    )

    st.markdown(
        f"""
        <div style="background: #18181b; border: 1px solid #27272a; border-radius: 6px; padding: 10px 14px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="status-badge {status_cls}">{status}</span>
                <span style="font-size: 0.75rem; font-family: monospace; color: #a1a1aa;">{active_id}</span>
            </div>
            <div style="font-size: 0.75rem; color: #71717a; font-family: monospace;">
                Layout: <span style="color: #d4d4d8;">{doc_type}</span> · Version: <span style="color: #d4d4d8;">v{doc.get('review_version', 0)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Arithmetic Validation Banner
    ev_resp = api_request("GET", f"/api/v1/documents/{active_id}/evidence")
    evidence = ev_resp.json() if ev_resp else {"rows": [], "total_checks": []}
    
    for check in evidence.get("total_checks", []):
        ptot = check.get("document_total", 0)
        rsum = check.get("rows_sum", 0)
        diff = check.get("difference", 0)
        cstat = check.get("status", "")

        if cstat == "MATCH":
            st.markdown(
                f"""
                <div class="banner-match">
                    <span>Balanced: Printed Total ({ptot:,} VND) matches calculated row sum ({rsum:,} VND).</span>
                    <span style="font-family: monospace; font-size: 0.75rem;">Delta: 0 VND</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="banner-mismatch">
                    <span>Discrepancy: Printed Total ({ptot:,} VND) differs from rows ({rsum:,} VND) by {diff:,} VND. Check for missed rows.</span>
                    <span style="font-family: monospace; font-size: 0.75rem; font-weight: 700;">MISMATCH</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Side-by-Side Review Workspace
    col_img, col_data = st.columns([1, 1], gap="large")

    with col_img:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #e4e4e7; margin-bottom: 8px;'>Source Scan & Evidence Overlay</div>", unsafe_allow_html=True)
        if doc.get("has_image"):
            img_data = api_request("GET", f"/api/v1/documents/{active_id}/image")
            if img_data:
                rows_meta = evidence.get("rows", [])
                choices = ["All bounding boxes"] + [f"Row {r['index'] + 1} (STT {r['stt']})" for r in rows_meta]
                picked = st.selectbox("Highlight", choices, key=f"overlay_pick_{active_id}", label_visibility="collapsed")
                row_idx = None if picked == "All bounding boxes" else choices.index(picked) - 1

                overlay = render_overlay(img_data.content, evidence, row_index=row_idx)
                st.image(overlay, use_container_width=True)
                
                # Minimalist legend
                st.markdown(
                    """
                    <div style="font-size: 0.7rem; color: #71717a; display: flex; gap: 12px; margin-top: 6px;">
                        <span><span style="color:#64748b;">■</span> STT</span>
                        <span><span style="color:#2563eb;">■</span> Description</span>
                        <span><span style="color:#16a34a;">■</span> Quantity</span>
                        <span><span style="color:#9333ea;">■</span> Unit</span>
                        <span><span style="color:#ea580c;">■</span> Price</span>
                        <span><span style="color:#dc2626;">■</span> Total</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div style="background: #18181b; border: 1px dashed #27272a; border-radius: 6px; padding: 24px; text-align: center; color: #71717a; font-size: 0.8rem;">
                    No source scan attached to this extraction.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_data:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #e4e4e7; margin-bottom: 8px;'>Extracted Line Items</div>", unsafe_allow_html=True)
        orig_items = doc.get("reviewed_items") or doc["raw_result"].get("items", [])
        cols = ["stt", "ten_dich_vu", "so_luong", "don_vi_tinh", "don_gia", "thanh_tien"]

        buffer = []
        for r in orig_items:
            details = r.get("payment_details")
            if isinstance(details, dict):
                details = {k: details.get(k) for k in ("chi_phi", "bhyt_chi", "so_giam", "benh_nhan_thanh_toan")}
            buffer.append({**{k: r.get(k) for k in cols}, "payment_details": details})

        df_grid = pd.DataFrame(
            [{k: v for k, v in row.items() if k != "payment_details"} for row in buffer],
            columns=cols,
        )

        edited_df = st.data_editor(
            df_grid,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key=f"editor_{active_id}",
        )

        # Real-time Arithmetic Calculation
        calc_sum = 0
        mismatch_rows = []
        for idx, row in edited_df.iterrows():
            try:
                q = float(row.get("so_luong", 0) or 0)
                p = float(row.get("don_gia", 0) or 0)
                t = float(row.get("thanh_tien", 0) or 0)
                calc_sum += t
                if round(q * p) != round(t):
                    mismatch_rows.append(f"Row {idx+1}")
            except Exception:
                pass

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #a1a1aa; padding: 4px 2px; border-bottom: 1px solid #27272a; margin-bottom: 12px;">
                <span>Calculated Rows Sum</span>
                <span style="font-family: monospace; font-weight: 600; color: #f4f4f5;">{calc_sum:,.0f} VND</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Row Count Difference Check (Rule R-303)
        count_diff = len(edited_df) != len(orig_items)
        reason_input = ""
        if count_diff:
            st.markdown("<div style='font-size:0.75rem; color:#fbbf24; font-weight:600; margin-bottom:2px;'>Row count modified (Rule R-303): written reason required</div>", unsafe_allow_html=True)
            reason_input = st.text_input("Reason", placeholder="e.g. Added row 3 missed by OCR parser.", key=f"reason_{active_id}", label_visibility="collapsed")

        # Operator sign-off
        c_op1, c_op2 = st.columns(2)
        with c_op1:
            reviewer_val = st.text_input("Reviewer ID", value=doc.get("reviewer_id") or "demo_operator")
        with c_op2:
            dtype_val = st.selectbox("Classification", ["MEDICINE_INVOICE", "MEDICAL_PAYMENT"], index=1 if doc_type == "MEDICAL_PAYMENT" else 0)

        ack = st.checkbox("Verified all values against original source document", key=f"ack_{active_id}")

        can_submit = status in {"PENDING_REVIEW", "BLOCKED_VALIDATION", "REVIEWED"}
        if st.button("Submit Verification", type="primary", use_container_width=True, disabled=not can_submit):
            if not ack:
                st.error("Verification confirmation required.")
            elif count_diff and len(reason_input.strip()) < 10:
                st.error("Reason of at least 10 characters required for row count changes.")
            else:
                cleaned = edited_df.to_dict(orient="records")
                try:
                    for i, r in enumerate(cleaned):
                        for f in ("stt", "so_luong", "don_gia", "thanh_tien"):
                            num = float(r[f])
                            if not num.is_integer():
                                raise ValueError(f)
                            r[f] = int(num)
                        src_det = buffer[i]["payment_details"] if i < len(buffer) else None
                        r["payment_details"] = src_det if dtype_val == "MEDICAL_PAYMENT" else None
                except Exception:
                    st.error("All numeric values must be whole numbers.")
                    st.stop()

                payload = {
                    "reviewer_id": reviewer_val.strip(),
                    "reviewed_document_type": dtype_val,
                    "confirm_names_and_values": True,
                    "items": cleaned,
                }
                if count_diff:
                    payload["row_count_change_reason"] = reason_input.strip()

                resp = api_request("PUT", f"/api/v1/documents/{active_id}/review", json=payload)
                if resp:
                    st.success("Verification saved. Status: REVIEWED.")
                    st.rerun()


# -----------------------------------------------------------------------------
# TAB 2: DOCUMENT QUEUE
# -----------------------------------------------------------------------------
elif active_nav == "Document Queue":
    st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #f4f4f5; margin-bottom: 4px;'>Document Queue</div>", unsafe_allow_html=True)
    st.caption("Active invoices in database with workflow status.")

    if not all_docs:
        st.info("No documents in database.")
    else:
        table_rows = []
        for d in all_docs:
            table_rows.append({
                "Document ID": d["id"],
                "Status": d["status"],
                "Layout": d.get("reviewed_document_type") or d.get("original_document_type", "UNKNOWN"),
                "RPA Ready": "Yes" if d.get("ready_for_rpa") else "No",
                "Created At": d.get("created_at", "")[:19].replace("T", " "),
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# TAB 3: FOUR-EYES APPROVAL
# -----------------------------------------------------------------------------
elif active_nav == "Four-Eyes Approval":
    st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #f4f4f5; margin-bottom: 4px;'>Four-Eyes Authorization (Rule R-302)</div>", unsafe_allow_html=True)
    st.caption("Separation of duties: approver must differ from the reviewer.")

    active_id = st.session_state.get("selected_document", "")
    if not active_id:
        st.info("Select a document in Workspace & Review first.")
        st.stop()

    resp = api_request("GET", f"/api/v1/documents/{active_id}")
    if not resp:
        st.stop()

    doc = resp.json()
    status = doc["status"]
    reviewer = doc.get("reviewer_id")

    if status == "REVIEWED":
        st.markdown(
            f"""
            <div class="card-panel">
                <div style="font-size: 0.8rem; color: #a1a1aa;">Verified by: <code style="color: #60a5fa;">{reviewer}</code></div>
                <div style="font-size: 0.75rem; color: #71717a; margin-top: 2px;">Review Version: v{doc.get('review_version', 1)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.dataframe(pd.DataFrame(doc.get("reviewed_items", [])), use_container_width=True, hide_index=True)

        approver_id = st.text_input("Approver ID*", placeholder="e.g. supervisor_ann")
        if approver_id and reviewer and approver_id.strip().casefold() == reviewer.strip().casefold():
            st.error("Rule R-302: Approver ID must differ from Reviewer ID.")

        ack = st.checkbox("Authorize document release for RPA export")
        valid = ack and approver_id.strip() and (not reviewer or approver_id.strip().casefold() != reviewer.strip().casefold())

        if st.button("Authorize Release", type="primary", disabled=not valid):
            app_resp = api_request(
                "POST",
                f"/api/v1/documents/{active_id}/approve",
                key=approver_key or None,
                json={"approver_id": approver_id.strip(), "acknowledge_review": True},
            )
            if app_resp:
                st.success("Authorized. Document is now APPROVED.")
                st.rerun()

    elif status == "APPROVED":
        st.markdown(
            f"""
            <div class="card-panel">
                <div style="font-size: 0.85rem; font-weight: 600; color: #34d399;">Approved & Released</div>
                <div style="font-size: 0.75rem; color: #71717a; font-family: monospace; margin-top: 4px;">SHA-256: {doc.get('approved_payload_sha256')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        csv_resp = api_request("GET", f"/api/v1/documents/{active_id}/export.csv")
        if csv_resp:
            st.download_button("Export Authoritative CSV", csv_resp.content, file_name=f"invoiceflow_{active_id}.csv", mime="text/csv", type="primary")

    else:
        st.info(f"Document is in status {status}. Complete review before approval.")


# -----------------------------------------------------------------------------
# TAB 4: ERP SIMULATOR
# -----------------------------------------------------------------------------
elif active_nav == "ERP Simulator":
    st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #f4f4f5; margin-bottom: 4px;'>Local ERP Simulator</div>", unsafe_allow_html=True)
    st.caption("Idempotent dispatch of approved CSV data into local simulated ERP.")

    active_id = st.session_state.get("selected_document", "")
    if not active_id:
        st.info("Select a document first.")
        st.stop()

    from invoiceflow_ai.rpa_handoff import get_demo_erp_rows, run_demo_worker, submit_approved_job

    rpa_db = "data/rpa_demo.sqlite3"
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("1. Submit to RPA Queue", use_container_width=True):
            try:
                with httpx.Client(base_url=api_url, timeout=30.0) as cl:
                    res = submit_approved_job(client=cl, api_headers={"X-API-Key": api_key}, document_id=active_id, db_path=rpa_db)
                st.success(f"Handoff: {res['action']}")
            except Exception as e:
                st.error(str(e))

    with col2:
        if st.button("2. Execute Worker", type="primary", use_container_width=True):
            try:
                res = run_demo_worker(document_id=active_id, db_path=rpa_db)
                st.success(f"Worker: {res['action']}")
            except Exception as e:
                st.error(str(e))

    with col3:
        if st.button("3. Test Duplicate Retry", use_container_width=True):
            try:
                res = run_demo_worker(document_id=active_id, db_path=rpa_db)
                if res["action"] == "ALREADY_SIMULATED":
                    st.success("Idempotency Confirmed: ALREADY_SIMULATED")
                else:
                    st.info(res["action"])
            except Exception as e:
                st.error(str(e))

    records = get_demo_erp_rows(document_id=active_id, db_path=rpa_db)
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# TAB 5: AUDIT LEDGER
# -----------------------------------------------------------------------------
elif active_nav == "Audit Ledger":
    st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #f4f4f5; margin-bottom: 4px;'>Governance Audit Ledger</div>", unsafe_allow_html=True)
    st.caption("Immutable chronological record of all document mutations.")

    active_id = st.session_state.get("selected_document", "")
    if active_id:
        aresp = api_request("GET", f"/api/v1/documents/{active_id}/audit")
        if aresp:
            for ev in aresp.json():
                st.markdown(
                    f"""
                    <div style="background: #18181b; border: 1px solid #27272a; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                        <div>
                            <span style="font-weight: 600; color: #f4f4f5;">{ev['action']}</span>
                            <span style="color: #71717a; margin-left: 8px;">Actor: <code style="color: #a1a1aa;">{ev['actor']}</code></span>
                        </div>
                        <span style="font-family: monospace; color: #71717a;">{(ev.get('created_at') or '')[:19].replace('T', ' ')}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("Details", expanded=False):
                    st.json(ev.get("details", {}))
