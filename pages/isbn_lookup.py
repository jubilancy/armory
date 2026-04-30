import streamlit as st
import pandas as pd
import requests
import time
import io
import re

def clean_isbn(isbn_raw):
    """Robust ISBN cleaning: removes dashes, spaces, and keeps only numbers/X."""
    return re.sub(r'[^0-9X]', '', str(isbn_raw).strip().upper())

def lookup_openlibrary(isbn):
    """Fetches book metadata from Open Library API."""
    try:
        # Try both 13 and 10 digit formats for better hit rates
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        key = list(data.keys())[0] if data else None
        if key:
            book = data[key]
            return {
                'ISBN': isbn,
                'Title': book.get('title', 'N/A'),
                'Author': ', '.join([a.get('name', '') for a in book.get('authors', [])]),
                'Publisher': book.get('publishers', [{}])[0].get('name', 'N/A') if isinstance(book.get('publishers'), list) and book.get('publishers') else 'N/A',
                'Year': book.get('publish_date', 'N/A'),
                'Source': 'Open Library'
            }
    except: pass
    return None

def run_app():
    st.set_page_config(page_title="ISBN Bulk Lookup", page_icon="📖")
    st.title("📖 ISBN Bulk Lookup")
    st.markdown("Fetch book metadata by pasting a list or uploading a CSV.")

    # Input Method Selection
    input_method = st.radio("Choose Input Method:", ["Paste List", "Upload CSV"], horizontal=True)
    
    isbns = []

    if input_method == "Paste List":
        raw_text = st.text_area(
            "Paste ISBNs (one per line):", 
            height=200, 
            placeholder="9780140449136\n0192801429\n978-0521618328"
        )
        if raw_text:
            lines = raw_text.split('\n')
            isbns = [clean_isbn(l) for l in lines if clean_isbn(l)]
    
    else:
        uploaded_file = st.file_uploader("Upload CSV (ISBNs in the first column)", type=['csv'])
        if uploaded_file:
            try:
                df_input = pd.read_csv(uploaded_file)
                # Take first column regardless of header name
                isbns = [clean_isbn(i) for i in df_input.iloc[:, 0].dropna() if clean_isbn(i)]
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # Process list
    if isbns:
        # Filter for valid ISBN lengths (10 or 13) and deduplicate
        isbns = [i for i in isbns if len(i) in [10, 13]]
        isbns = list(dict.fromkeys(isbns)) # Dedupe preserving order

        st.info(f"Ready to process {len(isbns)} unique valid ISBNs.")

        # Batch Search Trigger
        if st.button("Start Bulk Search", type="primary", use_container_width=True):
            results = []
            progress = st.progress(0)
            status = st.empty()

            for idx, isbn in enumerate(isbns):
                status.text(f"Searching {isbn} ({idx+1}/{len(isbns)})...")
                res = lookup_openlibrary(isbn)
                if res:
                    results.append(res)
                else:
                    # Append an entry even if not found so the user knows it failed
                    results.append({
                        'ISBN': isbn, 'Title': 'Not Found', 'Author': '', 
                        'Publisher': '', 'Year': '', 'Source': 'Open Library'
                    })
                
                progress.progress((idx + 1) / len(isbns))
                time.sleep(0.2) # API Rate limiting protection

            if results:
                df_final = pd.DataFrame(results)
                status.success(f"Complete! Found data for {len(df_final[df_final['Title'] != 'Not Found'])} books.")
                
                st.dataframe(df_final, use_container_width=True)
                
                # Export options
                csv_buffer = io.StringIO()
                df_final.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_data,
                    file_name="isbn_bulk_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )

if __name__ == "__main__":
    run_app()