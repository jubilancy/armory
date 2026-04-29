import streamlit as st

st.set_page_config(page_title="Tool Hub", layout="wide")

st.title("🛠️ Developer Tool Hub")
st.write("This hub centralizes various development and scraping scripts.")

st.info("Select a tool from the sidebar to get started.")

st.subheader("Current Inventory")
st.markdown("""
* **Letterboxd Scraper**: Scrape lists and movie data.
* **Open Library Explorer**: Search by ISBN or Author.
* **Digital Garden Tools**: Obsidian vault utilities.
""")