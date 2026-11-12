

import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime
from html import escape
import time

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="PulseNews - Live News Aggregator",
    page_icon="📰",
    layout="wide"
)

# ---------------- NEWS CATEGORIES ----------------

categories = {
    "🔥 Top Stories":
        "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",

    "💻 Technology":
        "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",

    "💼 Business":
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",

    "⚽ Sports":
        "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en"
}

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: #f8fafc;
}

header {
    background-color: #0f172a !important;
}

h1, h2, h3, p, label {
    color: #f8fafc;
}

.news-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #334155;
}

.news-title {
    color: #f8fafc;
    font-size: 18px;
    font-weight: bold;
    line-height: 1.5;
}

.news-date {
    color: #94a3b8;
    font-size: 13px;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
    height: 45px;
}

.stButton button:hover {
    background-color: #1d4ed8;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.title("📰 PulseNews Live")

st.caption("Your Daily Dose of Live News")

st.divider()

# ---------------- SESSION STATE ----------------

if "news_list" not in st.session_state:
    st.session_state.news_list = []

if "loaded_category" not in st.session_state:
    st.session_state.loaded_category = None

if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# ---------------- FETCH NEWS FUNCTION ----------------

def fetch_news(url):

    # New request on every button click
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=25
    ) as response:

        xml_data = response.read()

    root = ET.fromstring(xml_data)

    news_list = []

    for item in root.findall(".//item"):

        title = item.findtext("title")
        link = item.findtext("link")
        pub_date = item.findtext("pubDate")

        if not title:
            continue

        # Format published date
        try:
            published_date = parsedate_to_datetime(
                pub_date
            ).strftime("%d %b %Y, %I:%M %p")

        except Exception:
            published_date = "Date unavailable"

        news_list.append({
            "title": title,
            "link": link,
            "date": published_date
        })

        if len(news_list) >= 15:
            break

    return news_list


# ---------------- CATEGORY SELECTION ----------------

st.subheader("📂 Select News Category")

selected_category = st.selectbox(
    "Choose your preferred news category",
    list(categories.keys())
)

# ---------------- FETCH BUTTON ----------------

if st.button(
    "🔄 Fetch Latest News",
    use_container_width=True
):

    try:

        with st.spinner(
            f"Fetching latest {selected_category} news..."
        ):

            # Fetch selected category fresh
            fresh_news = fetch_news(
                categories[selected_category]
            )

            # Replace previous news
            st.session_state.news_list = fresh_news

            st.session_state.loaded_category = (
                selected_category
            )

            st.session_state.last_updated = (
                datetime.now().strftime(
                    "%d %b %Y, %I:%M:%S %p"
                )
            )

        if fresh_news:
            st.success(
                f"Loaded {len(fresh_news)} headlines successfully!"
            )
        else:
            st.warning(
                "No news available in this category right now."
            )

    except Exception as e:

        st.session_state.news_list = []
        st.session_state.loaded_category = selected_category

        st.error(
            "Unable to fetch news. Please check your internet connection and try again."
        )

        st.caption(f"Technical details: {e}")


# ---------------- DISPLAY NEWS ----------------

if st.session_state.loaded_category == selected_category:

    st.divider()

    st.subheader(
        f"📰 Latest News - {selected_category}"
    )

    if st.session_state.last_updated:

        st.caption(
            f"🕒 Last Updated: {st.session_state.last_updated}"
        )

    news_list = st.session_state.news_list

    if news_list:

        for index, news in enumerate(
            news_list,
            start=1
        ):

            safe_title = escape(news["title"])
            safe_date = escape(news["date"])

            safe_link = escape(
                news["link"] or "",
                quote=True
            )

            st.markdown(
                f"""
                <div class="news-card">

                    <div class="news-title">
                        {index}. {safe_title}
                    </div>

                    <p class="news-date">
                        🕒 Published: {safe_date}
                    </p>

                    <a href="{safe_link}"
                       target="_blank"
                       rel="noopener noreferrer">
                       Read Full Article ↗
                    </a>

                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "No headlines found. Please try again later."
        )

else:

    st.info(
        "Select a category and click Fetch Latest News."
    )


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    """
    <center>
        <p style="color:#94a3b8;">
            © 2026 PulseNews | Powered by Google News RSS
        </p>
    </center>
    """,
    unsafe_allow_html=True
)

