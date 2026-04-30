import streamlit as st
import json
import requests
from bs4 import BeautifulSoup

# Helper function to scrape Open Graph metadata (since spotify-url-info is JS-only)
def get_spotify_details(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Open Graph tags
    def get_og(prop):
        tag = soup.find("meta", property=prop)
        return tag["content"] if tag else None

    return {
        "url": url,
        "title": get_og("og:title"),
        "description": get_og("og:description"),
        "image": get_og("og:image"),
        "embedId": url.split('/')[-1].split('?')[0]
    }

def main():
    st.set_page_config(page_title="Spotify Metadata Extractor", page_icon="🎵")
    st.title("🎵 Spotify Metadata Extractor")
    st.write("Paste your Spotify URLs below (one per line).")

    # Text area for user input
    url_input = st.text_area("URLs", placeholder="https://open.spotify.com/track/...", height=200)

    if st.button("Extract Metadata"):
        urls = [u.strip() for u in url_input.split('\n') if u.strip()]
        
        if not urls:
            st.error("Please enter at least one URL.")
            return

        success = []
        errors = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, url in enumerate(urls):
            try:
                status_text.text(f"Processing: {url}")
                details = get_spotify_details(url)
                success.append(details)
            except Exception as e:
                errors.append({"url": url, "error": str(e)})
            
            progress_bar.progress((i + 1) / len(urls))

        status_text.text("Extraction Complete!")

        # Layout for download buttons
        col1, col2 = st.columns(2)
        
        if success:
            success_json = json.dumps(success, indent=2)
            col1.download_button(
                label="Download Success JSON",
                data=success_json,
                file_name="success.json",
                mime="application/json"
            )
            st.success(f"✅ Successfully processed {len(success)} links.")
            st.json(success[:3]) # Preview first 3

        if errors:
            errors_json = json.dumps(errors, indent=2)
            col2.download_button(
                label="Download Errors JSON",
                data=errors_json,
                file_name="errors.json",
                mime="application/json",
                help="Download a list of failed URLs and their reasons."
            )
            st.warning(f"❌ Encountered {len(errors)} errors.")

if __name__ == "__main__":
    main()
