

import streamlit as st
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="PulseNews | Live News",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================
# NEWS CATEGORIES
# =====================================

CATEGORIES = {
    "🔥 Top Stories":
        "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",

    "💻 Technology":
        "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",

    "💼 Business":
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",

    "⚽ Sports":
        "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en"
}

# =====================================
# CUSTOM DESIGN
# =====================================

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: #f8fafc;
}

header[data-testid="stHeader"] {
    background-color: #0f172a;
}

h1, h2, h3, p, label {
    color: #f8fafc;
}

.news-heading {
    font-size: 19px;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.5;
}

.news-date {
    color: #94a3b8;
    font-size: 13px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #1e293b;
    border-radius: 12px;
    border-color: #334155;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 9px;
    border: none;
    height: 45px;
    font-weight: bold;
}

.stButton button:hover {
    background-color: #1d4ed8;
    color: white;
}

a {
    color: #60a5fa !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================

st.title("📰 PulseNews Live")

st.caption("Your Daily Dose of Live News")

st.divider()

# =====================================
# SESSION STATE
# =====================================

if "news" not in st.session_state:
    st.session_state.news = []

if "loaded_category" not in st.session_state:
    st.session_state.loaded_category = None

if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

if "fetch_error" not in st.session_state:
    st.session_state.fetch_error = None

# =====================================
# NEWS FETCH FUNCTION
# =====================================

def fetch_latest_news(feed_url):

    headers = {
        "User-Agent": "Mozilla/5.0 PulseNews/1.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    response = requests.get(
        feed_url,
        headers=headers,
        timeout=25
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    news_items = []

    for item in root.findall(".//item"):

        title = item.findtext("title")
        link = item.findtext("link")
        pub_date = item.findtext("pubDate")

        if not title:
            continue

        try:
            published = parsedate_to_datetime(pub_date)

            published = published.strftime(
                "%d %b %Y, %I:%M %p"
            )

        except (TypeError, ValueError, OverflowError):
            published = "Date unavailable"

        news_items.append({
            "title": title,
            "link": link,
            "date": published
        })

        if len(news_items) == 15:
            break

    return news_items

# =====================================
# CATEGORY SELECTION
# =====================================

st.subheader("📂 Select News Category")

selected_category = st.selectbox(
    "Choose your preferred category",
    options=list(CATEGORIES.keys()),
    key="category_select"
)

# =====================================
# FETCH BUTTON
# =====================================

if st.button(
    "🔄 Fetch Latest News",
    use_container_width=True,
    type="primary"
):

    # Clear previous results immediately
    st.session_state.news = []
    st.session_state.loaded_category = selected_category
    st.session_state.fetch_error = None

    try:

        with st.spinner(
            f"Fetching latest {selected_category} news..."
        ):

            new_news = fetch_latest_news(
                CATEGORIES[selected_category]
            )

            st.session_state.news = new_news

            st.session_state.last_updated = datetime.now(
                ZoneInfo("Asia/Kolkata")
            ).strftime("%d %b %Y, %I:%M:%S %p")

    except requests.RequestException as error:

        st.session_state.fetch_error = (
            "Network error. Please check your internet connection "
            "and try again."
        )

    except ET.ParseError:

        st.session_state.fetch_error = (
            "Unable to read the news feed. Please try again."
        )

    except Exception as error:

        st.session_state.fetch_error = (
            f"Something went wrong: {error}"
        )

# =====================================
# DISPLAY NEWS
# =====================================

if st.session_state.loaded_category == selected_category:

    st.divider()

    st.subheader(
        f"📰 Latest News - {selected_category}"
    )

    if st.session_state.last_updated:

        st.caption(
            f"🕒 Last Updated: {st.session_state.last_updated}"
        )

    if st.session_state.fetch_error:

        st.error(st.session_state.fetch_error)

    elif st.session_state.news:

        st.success(
            f"Loaded {len(st.session_state.news)} headlines successfully!"
        )

        for number, news in enumerate(
            st.session_state.news,
            start=1
        ):

            with st.container(border=True):

                st.markdown(
                    f"**{number}. {news['title']}**"
                )

                st.caption(
                    f"🕒 Published: {news['date']}"
                )

                if news["link"]:
                    st.link_button(
                        "🔗 Read Full Article",
                        news["link"]
                    )

    else:

        st.warning(
            "No headlines available right now."
        )

else:

    st.info(
        "Select a news category and click Fetch Latest News."
    )

# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "© 2026 PulseNews | Powered by Google News RSS"
)

