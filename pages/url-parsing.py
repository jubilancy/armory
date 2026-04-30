import streamlit as st
from urllib.parse import urlparse
import pandas as pd
import io

def parse_urls(url_list):
    """Breaks down a list of URLs into structured components."""
    data = []
    for raw_url in url_list:
        url = raw_url.strip()
        if not url:
            continue
        
        # Ensure urlparse handles strings without schemes correctly
        # if no scheme is provided (e.g. google.com), netloc is empty.
        parsed = urlparse(url)
        
        data.append({
            "Full URL": url,
            "Scheme": parsed.scheme or "N/A",
            "Host": parsed.netloc or "N/A",
            "Path": parsed.path or "N/A",
            "Query": parsed.query or "N/A",
            "Params": parsed.params or "N/A"
        })
    return pd.DataFrame(data)

def run_app():
    st.set_page_config(page_title="URL Component Parser", page_icon="🔗")
    st.title("🔗 URL Component Parser")
    st.markdown("Paste a list of URLs to break them down into structured components (Scheme, Host, Path).")

    # Input: Text Area
    raw_input = st.text_area(
        "Paste URLs (one per line):", 
        height=250, 
        placeholder="https://github.com/andrejewski/himalaya\nhttps://streamlit.io/gallery\nwww.abebooks.com/search"
    )

    if raw_input:
        urls = [line.strip() for line in raw_input.split('\n') if line.strip()]
        
        if st.button("Parse URLs", type="primary", use_container_width=True):
            df = parse_urls(urls)
            
            if not df.empty:
                st.success(f"Parsed {len(df)} URLs successfully.")
                
                # Display Results
                st.dataframe(df, use_container_width=True)
                
                # Export: CSV
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download Parsed Results (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name="parsed_urls.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No valid URLs found to parse.")

if __name__ == "__main__":
    run_app()