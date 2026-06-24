import streamlit as st
import pandas as pd
from news_aggregator import fetch_news, RSS_FEEDS
from fake_news_detector import load_detector, analyze_article
import time

# Page config
st.set_page_config(
    page_title="AI News Aggregator & Fake News Detector",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .headline {
        color: #1f77b4;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .news-card {
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        background-color: white;
        transition: 0.3s;
    }
    .news-card:hover {
        transform: translateY(-3px);
    }
    .fake-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8em;
    }
    .real-badge {
        background-color: #4caf50;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8em;
    }
    .unknown-badge {
        background-color: #ff9800;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8em;
    }

    /* Credibility Score Colors */
    .credibility-high {
        color: #2ecc71;
        font-weight: bold;
        font-size: 1.1em;
    }
    .credibility-medium {
        color: #f39c12;
        font-weight: bold;
        font-size: 1.1em;
    }
    .credibility-low {
        color: #e74c3c;
        font-weight: bold;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📰 AI-Powered News Aggregator & Fake News Detector")
st.markdown("Get latest news + AI credibility score (Green = Trustworthy, Red = Risky)")

# Sidebar
st.sidebar.header("⚙ Controls")

topic_selection = st.sidebar.selectbox(
    "Select Topic:",
    options=list(RSS_FEEDS.keys()) + ["Custom Search"]
)

if topic_selection == "Custom Search":
    active_topic = st.sidebar.text_input("Enter topic:", "Artificial Intelligence")
else:
    active_topic = topic_selection

num_articles = st.sidebar.slider("Number of articles:", 1, 30, 10)

# Load AI model
detector = load_detector()

if detector is None:
    st.error("❌ AI model failed to load")

# Fetch button
if st.sidebar.button("🚀 Fetch News"):
    with st.spinner("Fetching & analyzing news..."):
        time.sleep(1)

        articles = fetch_news(active_topic, max_articles=num_articles)

        if not articles:
            st.warning("No news found")
        else:
            st.success(f"Found {len(articles)} articles")

            for article in articles:
                ai_result = analyze_article(detector, article['title'])

                prediction = ai_result.get('prediction', 'UNKNOWN')
                confidence = ai_result.get('confidence', 0.0)
                reason = ai_result.get('reason', '')

                # Badge logic
                if "fake" in prediction.lower():
                    badge_class = "fake-badge"
                    display_pred = "LIKELY FAKE"
                elif "real" in prediction.lower():
                    badge_class = "real-badge"
                    display_pred = "LIKELY REAL"
                else:
                    badge_class = "unknown-badge"
                    display_pred = "UNKNOWN"

                # Credibility Score Logic
                if "real" in prediction.lower():
                    credibility_score = confidence * 100
                elif "fake" in prediction.lower():
                    credibility_score = (1 - confidence) * 100
                else:
                    credibility_score = 50

                # Color mapping
                if credibility_score >= 70:
                    credibility_class = "credibility-high"
                elif credibility_score >= 40:
                    credibility_class = "credibility-medium"
                else:
                    credibility_class = "credibility-low"

                # UI Card
                with st.container():
                    st.markdown("<div class='news-card'>", unsafe_allow_html=True)

                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"### [{article['title']}]({article['link']})")
                        st.markdown(f"🗓 {article['published']}")
                        st.markdown(
                            article['summary'][:300] + "..."
                            if len(article['summary']) > 300 else article['summary']
                        )

                    with col2:
                        st.markdown("### 🤖 AI Result")
                        st.markdown(
                            f"<span class='{badge_class}'>{display_pred}</span>",
                            unsafe_allow_html=True
                        )

                        st.progress(float(confidence))

                        # Credibility Score Display
                        st.markdown(
                            f"<div class='{credibility_class}'>Credibility: {credibility_score:.1f}%</div>",
                            unsafe_allow_html=True
                        )

                        # Optional explanation
                        if reason and "fake" in prediction.lower():
                            st.caption(f"⚠ {reason}")

                    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
