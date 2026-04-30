import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import io
import re

# Cache the scraping function to prevent excessive calls to AbeBooks
@st.cache_data(show_spinner=False)
def scrape_abebooks(base_store_url, limit_pages=5):
    # Standard headers to avoid blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Try to extract vendor ID (vci) if a full URL is provided, otherwise use the input as the base
    # Example target: https://www.abebooks.com/servlet/SearchResults?vci=59656139&sortby=0
    if "vci=" in base_store_url:
        vci_match = re.search(r'vci=(\d+)', base_store_url)
        if vci_match:
            vci = vci_match.group(1)
            base_url = f"https://www.abebooks.com/servlet/SearchResults?vci={vci}&sortby=0"
        else:
            base_url = base_store_url
    else:
        base_url = base_store_url

    books_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for page in range(1, limit_pages + 1):
        status_text.text(f"Scraping page {page} of {limit_pages}...")
        url = f"{base_url}&cp={page}"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('li', class_='result-item')
            
            if not results:
                break

            for item in results:
                title_meta = item.find('meta', itemprop='name')
                author_meta = item.find('meta', itemprop='author')
                
                isbn = "N/A"
                isbn_meta = item.find('meta', itemprop='isbn')
                
                if isbn_meta and isbn_meta.get('content'):
                    isbn = isbn_meta['content']
                else:
                    attributes = item.find_all(['span', 'li'], class_='item-attribute')
                    for attr in attributes:
                        if "ISBN" in attr.text:
                            isbn = ''.join(filter(str.isdigit, attr.text))
                            break

                if title_meta:
                    books_data.append({
                        "Book": title_meta['content'],
                        "Author": author_meta['content'] if author_meta else "N/A",
                        "ISBN": isbn
                    })

            progress_bar.progress(page / limit_pages)
            time.sleep(1.5) # Politeness delay

        except Exception as e:
            st.error(f"Error on page {page}: {e}")
            break
    
    status_text.empty()
    progress_bar.empty()
    return pd.DataFrame(books_data)

def run_app():
    st.set_page_config(page_title="AbeBooks Catalog Scraper", page_icon="📚")
    st.title("📚 AbeBooks Store Catalog")
    st.markdown("Enter a Store URL or a Search Result URL from AbeBooks to extract the catalog.")

    # Main Input Section
    store_url = st.text_input(
        "AbeBooks Store/Search URL:", 
        value="https://www.abebooks.com/servlet/SearchResults?vci=59656139&sortby=0",
        help="Paste the URL of the store or search results you want to scrape."
    )

    # Sidebar settings
    st.sidebar.header("Scraper Settings")
    page_limit = st.sidebar.slider("Pages to scrape", 1, 25, 5)
    
    if st.button("Start Catalog Extraction", type="primary"):
        if not store_url:
            st.error("Please enter a valid AbeBooks URL.")
            return

        with st.spinner("Fetching data from AbeBooks..."):
            df = scrape_abebooks(store_url, page_limit)
            
            if not df.empty:
                st.success(f"Successfully grabbed {len(df)} books!")
                
                # Display data
                st.dataframe(df, use_container_width=True)
                
                # Convert for download
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Catalog as CSV",
                    data=csv_data,
                    file_name="abebooks_catalog.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data was collected. Check the connection or URL. Ensure the URL contains a valid vendor ID (vci).")

if __name__ == "__main__":
    run_app()