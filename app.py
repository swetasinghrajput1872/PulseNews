


import streamlit as st
import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="PulseNews Live",
    page_icon="📰",
    layout="wide"
)

# =====================================
# CATEGORY SEARCH QUERIES
# =====================================

CATEGORIES = {
    "🔥 Top Stories": "India OR world when:1d",
    "💻 Technology": "Technology when:1d",
    "💼 Business": "Business when:1d",
    "⚽ Sports": "Sports when:1d"
}

# =====================================
# CUSTOM CSS
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

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 9px;
    height: 45px;
    font-weight: bold;
}

.stButton button:hover {
    background-color: #1d4ed8;
    color: white;
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

if "error" not in st.session_state:
    st.session_state.error = None

# =====================================
# FETCH LATEST NEWS FUNCTION
# =====================================

def fetch_latest_news(query):

    base_url = "https://news.google.com/rss/search"

    params = {
        "q": query,
        "hl": "en-IN",
        "gl": "IN",
        "ceid": "IN:en"
    }

    url = base_url + "?" + urlencode(params)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=25
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    articles = []

    for item in root.findall(".//item"):

        title = item.findtext("title")
        link = item.findtext("link")
        pub_date = item.findtext("pubDate")

        if not title:
            continue

        try:
            date_obj = parsedate_to_datetime(pub_date)

            if date_obj.tzinfo is None:
                date_obj = date_obj.replace(
                    tzinfo=timezone.utc
                )

            articles.append({
                "title": title,
                "link": link,
                "date": date_obj,
                "date_text": date_obj.astimezone(
                    timezone.utc
                ).strftime("%d %b %Y, %I:%M %p UTC")
            })

        except (TypeError, ValueError, OverflowError):
            continue

    # Newest articles first
    articles.sort(
        key=lambda article: article["date"],
        reverse=True
    )

    return articles[:15]

# =====================================
# CATEGORY SELECTION
# =====================================

st.subheader("📂 Select News Category")

selected_category = st.selectbox(
    "Choose News Category",
    list(CATEGORIES.keys())
)

# =====================================
# FETCH BUTTON
# =====================================

if st.button(
    "🔄 Fetch Latest News",
    use_container_width=True,
    type="primary"
):

    # Remove previous results
    st.session_state.news = []
    st.session_state.loaded_category = selected_category
    st.session_state.last_updated = None
    st.session_state.error = None

    try:

        with st.spinner(
            "Searching for the latest news..."
        ):

            articles = fetch_latest_news(
                CATEGORIES[selected_category]
            )

            st.session_state.news = articles

            st.session_state.last_updated = (
                datetime.now().strftime(
                    "%d %b %Y, %I:%M:%S %p"
                )
            )

    except Exception as e:

        st.session_state.error = str(e)

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
            f"🕒 Last Updated: "
            f"{st.session_state.last_updated}"
        )

    if st.session_state.error:

        st.error(
            "Unable to fetch news. Please try again."
        )

    elif st.session_state.news:

        st.success(
            f"Loaded {len(st.session_state.news)} latest headlines!"
        )

        for index, article in enumerate(
            st.session_state.news,
            start=1
        ):

            with st.container(border=True):

                st.markdown(
                    f"**{index}. {article['title']}**"
                )

                st.caption(
                    f"🕒 Published: {article['date_text']}"
                )

                if article["link"]:

                    st.link_button(
                        "🔗 Read Full Article",
                        article["link"]
                    )

    else:

        st.warning(
            "No recent news found in the last 24 hours."
        )

else:

    st.info(
        "Select a category and click Fetch Latest News."
    )

# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "© 2026 PulseNews | Powered by Google News RSS"
)
