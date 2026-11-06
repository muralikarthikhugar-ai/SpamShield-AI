
import streamlit as st
import requests
import pandas as pd

# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="SpamShield AI",
    page_icon="🛡️",
    layout="wide"
)

API_URL = "http://127.0.0.1:5000"

# ----------------------------------
# CUSTOM CSS
# ----------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #00D4AA;
}

.subtitle {
    text-align: center;
    color: #AAAAAA;
    font-size: 16px;
}

</style>
""", unsafe_allow_html=True)


# ----------------------------------
# FLASK HEALTH CHECK
# ----------------------------------

@st.cache_data(ttl=5)
def check_flask_health():
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=3
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:
        return None


health = check_flask_health()

# ----------------------------------
# SIDEBAR - API STATUS
# ----------------------------------

st.sidebar.title("🛡️ SpamShield AI")
st.sidebar.subheader("API Monitoring")

if health:
    st.sidebar.success("🟢 Flask Connected")

    st.sidebar.write("**API Status:**", health.get("status", "Unknown"))

    model_loaded = health.get("model_loaded", False)

    if model_loaded:
        st.sidebar.success("🧠 ML Model Loaded")
    else:
        st.sidebar.error("ML Model Not Loaded")

    st.sidebar.write(
        "**Model:**",
        health.get("model_name", "Unknown")
    )

    st.sidebar.write("**API URL:**", API_URL)

else:
    st.sidebar.error("🔴 Flask Disconnected")
    st.sidebar.warning(
        "Start your Flask server using: uv run python app.py"
    )

if st.sidebar.button("🔄 Refresh API Status"):
    check_flask_health.clear()
    st.rerun()


# ----------------------------------
# HEADER
# ----------------------------------

st.markdown(
    '<div class="main-title">🛡️ SpamShield AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Intelligent SMS Spam Detection System</div>',
    unsafe_allow_html=True
)

st.divider()

# ----------------------------------
# API HEALTH OVERVIEW
# ----------------------------------

st.subheader("System Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Flask API",
        "Connected" if health else "Disconnected"
    )

with col2:
    st.metric(
        "Model Status",
        "Loaded" if health and health.get("model_loaded") else "Unavailable"
    )

with col3:
    st.metric(
        "ML Algorithm",
        health.get("model_name", "Unavailable") if health else "Unavailable"
    )

st.divider()


# ----------------------------------
# DETECTION TABS
# ----------------------------------

single_tab, batch_tab = st.tabs([
    "📩 Single SMS Detection",
    "📚 Batch SMS Detection"
])


# ==================================
# SINGLE MESSAGE DETECTION
# ==================================

with single_tab:

    st.subheader("Check Individual SMS")

    message = st.text_area(
        "Enter your SMS message:",
        placeholder="Paste your SMS message here...",
        height=150,
        key="single_message"
    )

    if st.button("🔍 Detect Spam", use_container_width=True):

        if not health:
            st.error("Flask API is not connected.")

        elif not message.strip():
            st.warning("Please enter a message.")

        else:
            try:
                response = requests.post(
                    f"{API_URL}/predict",
                    json={"message": message},
                    timeout=10
                )

                if response.status_code == 200:

                    result = response.json()

                    prediction = result["prediction"]

                    st.divider()
                    st.subheader("Detection Result")

                    if prediction == "SPAM":
                        st.error("🚨 SPAM MESSAGE DETECTED")
                    else:
                        st.success("✅ MESSAGE CLASSIFIED AS HAM")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Spam Probability",
                            f'{result["spam_probability"]}%'
                        )

                    with col2:
                        st.metric(
                            "Ham Probability",
                            f'{result["ham_probability"]}%'
                        )

                    st.caption("Prediction generated using Linear SVM.")

                else:
                    st.error(f"API Error: {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")


# ==================================
# BATCH MESSAGE DETECTION
# ==================================

with batch_tab:

    st.subheader("Batch SMS Detection")

    st.write(
        "Enter multiple SMS messages below. "
        "Put each message on a separate line."
    )

    batch_messages = st.text_area(
        "Enter SMS messages:",
        placeholder="""Congratulations! You won a free gift. Claim now!
Hey, are you coming to college tomorrow?
Your OTP is 456789. Do not share it with anyone.""",
        height=220,
        key="batch_messages"
    )

    messages = [
        msg.strip()
        for msg in batch_messages.splitlines()
        if msg.strip()
    ]

    st.caption(f"Messages entered: {len(messages)} / 500")

    if st.button("🚀 Analyze All Messages", use_container_width=True):

        if not health:
            st.error("Flask API is not connected.")

        elif not messages:
            st.warning("Please enter at least one message.")

        elif len(messages) > 500:
            st.error("Maximum 500 messages allowed.")

        else:
            try:
                with st.spinner("Analyzing messages..."):

                    response = requests.post(
                        f"{API_URL}/predict/batch",
                        json={"messages": messages},
                        timeout=30
                    )

                if response.status_code == 200:

                    data = response.json()
                    results = data["results"]

                    st.success(
                        f"Successfully analyzed {len(results)} messages!"
                    )

                    spam_count = sum(
                        1 for item in results
                        if item["prediction"] == "SPAM"
                    )

                    ham_count = len(results) - spam_count

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Total Messages", len(results))

                    with col2:
                        st.metric("Spam Messages", spam_count)

                    with col3:
                        st.metric("Ham Messages", ham_count)

                    st.divider()
                    st.subheader("Batch Prediction Results")

                    df = pd.DataFrame(results)

                    df.index = range(1, len(df) + 1)
                    df.index.name = "No."

                    st.dataframe(
                        df,
                        use_container_width=True
                    )

                    csv = df.to_csv(index=True).encode("utf-8")

                    st.download_button(
                        "⬇️ Download Results as CSV",
                        data=csv,
                        file_name="spamshield_batch_results.csv",
                        mime="text/csv"
                    )

                else:
                    st.error(f"API Error: {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")


# ----------------------------------
# FOOTER
# ----------------------------------

st.divider()

st.markdown(
    "<center>SpamShield AI | Python • Scikit-learn • Flask • Streamlit</center>",
    unsafe_allow_html=True
)
