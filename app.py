
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET

# Page configuration
st.set_page_config(
    page_title="PulseNews - Live News Aggregator",
    page_icon="📰",
    layout="centered"
)

# News categories
categories = {
    "🔥 Top Stories": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "💻 Technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "💼 Business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "⚽ Sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en"
}

# Custom CSS
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: #f8fafc;
}

h1, h2, h3, p, label {
    color: #f8fafc !important;
}

.news-card {
    background-color: #1e293b;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 12px;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("📰 PulseNews Live")
st.markdown(
    "<center>Your Daily Dose of Live News</center>",
    unsafe_allow_html=True
)

st.write("---")

# Category selection
selected_category = st.selectbox(
    "📂 Select News Category",
    list(categories.keys())
)

# Fetch news function
@st.cache_data(ttl=300)
def fetch_news(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    news_list = []

    for item in root.findall(".//item")[:15]:
        title = item.findtext("title")
        link = item.findtext("link")

        if title:
            news_list.append({
                "title": title,
                "link": link
            })

    return news_list


# Refresh button
if st.button("🔄 Fetch Latest News", use_container_width=True):
    fetch_news.clear()

# Display news
try:
    with st.spinner("Fetching latest headlines..."):

        news_list = fetch_news(
            categories[selected_category]
        )

    st.success(
        f"Loaded {len(news_list)} headlines successfully!"
    )

    for index, news in enumerate(news_list, start=1):

        with st.container(border=True):

            st.markdown(
                f"### {index}. {news['title']}"
            )

            if news["link"]:
                st.link_button(
                    "Read Full Story ↗",
                    news["link"]
                )

    if not news_list:
        st.warning("No headlines available right now.")

except Exception:
    st.error(
        "Unable to fetch news. Please check your internet connection."
    )

# Footer
st.write("---")

st.markdown(
    "<center>© 2026 PulseNews | Live News Aggregator</center>",
    unsafe_allow_html=True
)
