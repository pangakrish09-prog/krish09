import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "a3f417b116fa4104b3c547e8ee9d32e1"
BASE_URL = "https://newsapi.org/v2/top-headlines"

st.set_page_config(
    page_title="Advanced News Explorer",
    page_icon="📰",
    layout="wide"
)

# -----------------------------
# FUNCTIONS
# -----------------------------
@st.cache_data(ttl=300)
def fetch_news(country, category, page_size, keyword):
    params = {
        "apiKey": API_KEY,
        "country": country,
        "pageSize": page_size
    }

    if category != "all":
        params["category"] = category

    if keyword.strip():
        params["q"] = keyword

    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


# -----------------------------
# HEADER
# -----------------------------
st.title("📰 Advanced News Explorer")
st.markdown("Search and filter real-time headlines using NewsAPI")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

country_options = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp"
}

selected_country = st.sidebar.selectbox(
    "Location",
    list(country_options.keys())
)

selected_category = st.sidebar.selectbox(
    "Topic",
    [
        "all",
        "business",
        "entertainment",
        "general",
        "health",
        "science",
        "sports",
        "technology"
    ]
)

num_articles = st.sidebar.slider(
    "Number of Articles",
    min_value=5,
    max_value=100,
    value=20,
    step=5
)

keyword = st.sidebar.text_input(
    "Search Keywords",
    placeholder="e.g. AI, Tesla, Cricket..."
)

search_btn = st.sidebar.button("🔍 Fetch News")

# -----------------------------
# FETCH NEWS
# -----------------------------
if search_btn:
    try:
        with st.spinner("Fetching latest headlines..."):
            data = fetch_news(
                country_options[selected_country],
                selected_category,
                num_articles,
                keyword
            )

        articles = data.get("articles", [])

        if not articles:
            st.warning("No articles found.")
            st.stop()

        st.success(f"Found {len(articles)} articles")

        # -----------------------------
        # SUMMARY TABLE
        # -----------------------------
        records = []

        for article in articles:
            records.append({
                "Title": article.get("title"),
                "Source": article.get("source", {}).get("name"),
                "Published": article.get("publishedAt", "")[:10]
            })

        df = pd.DataFrame(records)

        with st.expander("📊 Article Summary"):
            st.dataframe(df, use_container_width=True)

        # -----------------------------
        # ARTICLE CARDS
        # -----------------------------
        st.subheader("Latest Headlines")

        for article in articles:
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])

                image_url = article.get("urlToImage")

                with col1:
                    if image_url:
                        st.image(image_url, use_container_width=True)

                with col2:
                    st.markdown(
                        f"### {article.get('title', 'No Title')}"
                    )

                    source = article.get("source", {}).get("name", "Unknown")
                    author = article.get("author", "Unknown")
                    published = article.get("publishedAt", "")

                    try:
                        published = datetime.fromisoformat(
                            published.replace("Z", "+00:00")
                        ).strftime("%d %b %Y %H:%M")
                    except:
                        pass

                    st.caption(
                        f"Source: {source} | Author: {author} | Published: {published}"
                    )

                    description = article.get("description")
                    if description:
                        st.write(description)

                    if article.get("url"):
                        st.link_button(
                            "Read Full Article",
                            article["url"]
                        )

        # -----------------------------
        # DOWNLOAD RESULTS
        # -----------------------------
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Headlines CSV",
            data=csv,
            file_name="news_headlines.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Choose filters from the sidebar and click 'Fetch News'.") 
