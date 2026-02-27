import streamlit as st
from pdf_utils import extract_text
from text_utils import chunk_text
from llm import insurance_decoder

st.set_page_config(
    page_title="Insurance Policy Decoder",
    layout="wide"
)

st.title("Insurance Policy Decoder")
st.write(
    "Upload your insurance policy to understand risks, exclusions, "
    "waiting periods and hidden financial impacts."
)


def safe_dict(item):
    """
    Ensures LLM output never crashes UI.
    Converts string → dictionary safely.
    """
    if isinstance(item, dict):
        return item
    return {"value": str(item)}

uploaded_file = st.file_uploader(
    "Upload Insurance Policy (PDF)",
    type=["pdf"]
)

if uploaded_file:

    with st.spinner("Reading policy document..."):
        text = extract_text(uploaded_file)

    if not text:
        st.error("No readable text found.")
        st.stop()

    chunks = chunk_text(text)

    all_alerts = []
    waiting_periods = []
    exclusions = []
    copayments = []
    hidden_limits = []

    total_risk = 0
    valid_chunks = 0

    progress = st.progress(0)

    with st.spinner("Decoding Insurance Policy..."):

        for i, chunk in enumerate(chunks):

            result = insurance_decoder(chunk)

            if result:

                chunk_score = result.get("risk_score", 0)
                total_risk = max(total_risk, chunk_score)
                valid_chunks += 1

                all_alerts.extend(result.get("danger_alerts", []))
                waiting_periods.extend(result.get("waiting_periods", []))
                exclusions.extend(result.get("exclusions", []))
                copayments.extend(result.get("co_payment", []))
                hidden_limits.extend(result.get("hidden_limits", []))

            progress.progress((i + 1) / len(chunks))

    if valid_chunks == 0:
        st.error("Policy analysis failed.")
        st.stop()

    avg_risk = min(100, max(total_risk, 0))


    st.markdown("## Overall Policy Risk Score")
    st.metric("Risk Score (0–100)", avg_risk)

    if avg_risk > 75:
        st.error("HIGH CLAIM REJECTION RISK")
    elif avg_risk > 50:
        st.warning("Moderate Risk Policy")
    else:
        st.success("Relatively Safe Policy")

    priority = {"Critical": 3, "High": 2, "Medium": 1}

    all_alerts = sorted(
        all_alerts,
        key=lambda x: priority.get(
            x.get("severity", "Medium")
            if isinstance(x, dict)
            else "Medium",
            0
        ),
        reverse=True
    )

    st.markdown("## Immediate Attention Required")

    for alert in all_alerts:
        alert = safe_dict(alert)

        message = alert.get("message") or alert.get("value", "")
        severity = alert.get("severity", "Medium")

        if severity == "Critical":
            st.error(message)
        elif severity == "High":
            st.warning(message)
        else:
            st.info(message)

    st.markdown("## Waiting Period Risks")

    for wp in waiting_periods:
        wp = safe_dict(wp)

        st.warning(f"""
**Condition:** {wp.get('condition', wp.get('value',''))}

⏱ Duration: {wp.get('duration','')}

⚠ Impact:
{wp.get('impact','')}
""")

    st.markdown("## Treatments Not Covered")

    for ex in exclusions:
        ex = safe_dict(ex)

        st.error(f"""
**Excluded Item:** {ex.get('item', ex.get('value',''))}

Financial Risk:
{ex.get('impact','')}
""")

    st.markdown("## Out-of-Pocket Costs")

    for cp in copayments:
        cp = safe_dict(cp)

        st.warning(f"""
**Co-payment:** {cp.get('percentage', cp.get('value',''))}

You May Pay:
{cp.get('impact','')}
""")

    st.markdown("## Hidden Coverage Limits")

    for hl in hidden_limits:
        hl = safe_dict(hl)

        st.info(f"""
**Limit:** {hl.get('limit', hl.get('value',''))}

Impact:
{hl.get('impact','')}
""")

    st.success("Policy decoding completed successfully!")