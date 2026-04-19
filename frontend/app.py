import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Bank Name Change Verification", layout="wide")

# ---------------------------
# HELPERS
# ---------------------------
def format_status(status):
    if status == "AI_VERIFIED_PENDING_HUMAN":
        return "🟡 Needs Review"
    elif status == "APPROVED":
        return "🟢 Approved"
    elif status == "REJECTED":
        return "🔴 Rejected"
    else:
        return "⚠️ Escalated"

def confidence_badge(score):
    if score > 85:
        return ("success", "High confidence match")
    elif score > 60:
        return ("warning", "Medium confidence — needs review")
    else:
        return ("error", "Low confidence — likely mismatch")

# ---------------------------
# HEADER
# ---------------------------
st.title("🧠 AI Name Change Verification System")

# ---------------------------
# SUBMIT FORM
# ---------------------------
st.subheader("📤 Submit Name Change Request")

with st.form("submit_form"):
    col1, col2 = st.columns(2)

    with col1:
        customer_id = st.text_input("Customer ID")
        old_name = st.text_input("Old Name")

    with col2:
        new_name = st.text_input("New Name")
        file = st.file_uploader("Upload Document (.docx)", type=["docx"])

    submit = st.form_submit_button("Submit Request")

    if submit:
        if not file:
            st.error("Please upload a document")
        else:
            files = {"file": (file.name, file.getvalue())}
            data = {
                "customer_id": customer_id,
                "old_name": old_name,
                "new_name": new_name
            }

            res = requests.post(f"{BASE_URL}/submit", data=data, files=files)

            if res.status_code == 200:
                st.success("✅ Request Submitted Successfully")
                st.rerun()
            else:
                st.error("❌ Submission Failed")

# ---------------------------
# API CALLS
# ---------------------------
def get_pending():
    return requests.get(f"{BASE_URL}/pending").json()

def get_processed():
    return requests.get(f"{BASE_URL}/processed").json()

def approve(id):
    requests.post(f"{BASE_URL}/approve?id={id}")

def reject(id):
    requests.post(f"{BASE_URL}/reject?id={id}")

# ---------------------------
# PENDING SECTION
# ---------------------------
st.divider()
st.subheader("🟡 Pending Requests")

pending = get_pending()

if not pending:
    st.info("No pending requests")
else:
    for req in pending:
        st.markdown("---")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**ID:** {req['id']}")
            st.write(f"**Customer:** {req['customer_id']}")
            st.write(f"**Old Name:** {req['old_name']}")
            st.write(f"**New Name:** {req['new_name']}")
            st.write(f"**Confidence:** {round(req['confidence'], 2)}")

            st.markdown("### 🤖 AI Signals")

            level, msg = confidence_badge(req["confidence"])
            if level == "success":
                st.success(msg)
            elif level == "warning":
                st.warning(msg)
            else:
                st.error(msg)

            if req["forgery"] == "REVIEW":
                st.warning("⚠️ AI flagged potential issue")
            else:
                st.success("✅ No issues detected in document")

            st.markdown("### 🧠 AI Explanation")
            st.info(req["summary"])

        with col2:
            st.write("### 👨‍💼 Actions")

            if st.button(f"Approve {req['id']}"):
                approve(req["id"])
                st.success("Approved")
                st.rerun()

            if st.button(f"Reject {req['id']}"):
                reject(req["id"])
                st.error("Rejected")
                st.rerun()

# ---------------------------
# PROCESSED SECTION
# ---------------------------
st.divider()
st.subheader("🟢 Processed Requests")

processed = get_processed()

if not processed:
    st.info("No processed requests")
else:
    for req in processed:
        st.markdown("---")

        st.write(f"**ID:** {req['id']}")
        st.write(f"**Customer:** {req['customer_id']}")
        st.write(f"**Old Name:** {req['old_name']}")
        st.write(f"**New Name:** {req['new_name']}")
        st.write(f"**Confidence:** {round(req['confidence'], 2)}")

        # ---------------------------
        # FINAL DECISION (PRIMARY)
        # ---------------------------
        st.markdown("## 👨‍⚖️ Final Decision")
        st.markdown(f"## {format_status(req['status'])}")

        if req["status"] == "APPROVED":
            st.success("Approved by human checker (AI recommendation overridden if needed)")
        elif req["status"] == "REJECTED":
            st.error("Rejected by human checker")
        else:
            st.warning("Escalated for further verification")

        # ---------------------------
        # AI SIGNALS (SECONDARY)
        # ---------------------------
        st.markdown("### 🤖 AI Signals (Before Human Review)")

        level, msg = confidence_badge(req["confidence"])
        if level == "success":
            st.success(msg)
        elif level == "warning":
            st.warning(msg)
        else:
            st.error(msg)

        if req["forgery"] == "REVIEW":
            st.warning("⚠️ AI flagged potential issue (reviewed by human)")
        else:
            st.success("✅ Passed AI verification")

        # ---------------------------
        # AI EXPLANATION
        # ---------------------------
        st.markdown("### 🧠 AI Explanation")
        st.info(req["summary"])