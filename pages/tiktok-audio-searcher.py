import streamlit as st
import pandas as pd
import time
import io
import random
import re

# Mock data to match your original JS logic
SAMPLE_AUDIO_DATA = [
    {"title": "As It Was", "artist": "Harry Styles", "musicId": "7063948643480488709"},
    {"title": "Build a B***h", "artist": "Bella Poarch", "musicId": "7054387291847263235"},
    {"title": "Good 4 U", "artist": "Olivia Rodrigo", "musicId": "7089234567890123456"},
    {"title": "Levitating", "artist": "Dua Lipa", "musicId": "7078345678901234567"},
    {"title": "Stay", "artist": "The Kid LAROI & Justin Bieber", "musicId": "7067456789012345678"},
    {"title": "Industry Baby", "artist": "Lil Nas X & Jack Harlow", "musicId": "7056567890123456789"},
    {"title": "Heat Waves", "artist": "Glass Animals", "musicId": "7045678901234567890"},
    {"title": "Bad Habit", "artist": "Steve Lacy", "musicId": "7034789012345678901"},
    {"title": "About Damn Time", "artist": "Lizzo", "musicId": "7023890123456789012"},
    {"title": "Running Up That Hill", "artist": "Kate Bush", "musicId": "7012901234567890123"}
]

ERROR_MESSAGES = [
    "Invalid TikTok URL format",
    "Video not found or private",
    "Audio metadata unavailable",
    "Rate limit exceeded",
    "Network timeout"
]

# Simulated common browser User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

# Simulated Proxies
PROXIES = [
    "192.168.1.1:8080",
    "45.33.22.11:3128",
    "104.248.12.34:80",
    "178.128.90.12:1080",
    "Direct Connection"
]

def is_valid_tiktok(url):
    pattern = r'^https?://(www\.)?tiktok\.com/@[\w.-]+/video/\d+'
    return re.match(pattern, url.strip())

def process_url_with_retry(url, max_retries, jitter_range, use_proxies):
    """Handles the extraction logic with retry mechanism and proxy rotation."""
    attempts = 0
    while attempts <= max_retries:
        # Simulate Request with Jitter (Wait time grows if it's a retry)
        wait_time = random.uniform(jitter_range[0], jitter_range[1]) * (attempts + 1)
        time.sleep(wait_time)
        
        current_ua = random.choice(USER_AGENTS)
        current_proxy = random.choice(PROXIES) if use_proxies else "N/A"
        
        # 85% success rate simulation
        if random.random() > 0.15:
            data = random.choice(SAMPLE_AUDIO_DATA)
            return {
                "URL": url,
                "Title": data["title"],
                "Artist": data["artist"],
                "Music ID": data["musicId"],
                "Status": "✅ Success",
                "Retries": attempts,
                "UA Used": current_ua.split(')')[0] + ')',
                "Proxy": current_proxy
            }
        
        attempts += 1
        if attempts > max_retries:
            return {
                "URL": url,
                "Title": "N/A",
                "Artist": "N/A",
                "Music ID": "N/A",
                "Status": f"❌ {random.choice(ERROR_MESSAGES)}",
                "Retries": max_retries,
                "UA Used": current_ua.split(')')[0] + ')',
                "Proxy": current_proxy
            }

def run_app():
    st.set_page_config(page_title="TikTok Audio Extractor", page_icon="🎵")
    st.title("🎵 TikTok Audio Metadata Extractor")
    st.markdown("Extract song titles and artist info from TikTok URLs in bulk.")

    # Sidebar: Anti-Rate Limit Controls
    st.sidebar.header("🛡️ Anti-Rate Limit Settings")
    batch_size = st.sidebar.number_input("Batch Size", min_value=1, max_value=50, value=5)
    cooldown = st.sidebar.slider("Batch Cooldown (seconds)", 1, 10, 3)
    jitter_range = st.sidebar.slider("Request Jitter (seconds)", 0.1, 5.0, (0.5, 1.5))
    
    st.sidebar.header("🔄 Resilience Settings")
    use_proxies = st.sidebar.checkbox("Enable Proxy Rotation", value=True)
    max_retries = st.sidebar.slider("Max Retries for Failures", 0, 5, 2)

    # Input Section
    input_method = st.radio("Input Method", ["Paste URLs", "Upload File"], horizontal=True)
    urls = []

    if input_method == "Paste URLs":
        raw_urls = st.text_area("Paste URLs (one per line):", height=200, placeholder="https://www.tiktok.com/@user/video/123...")
        if raw_urls:
            urls = [u.strip() for u in raw_urls.split('\n') if is_valid_tiktok(u)]
    else:
        uploaded_file = st.file_uploader("Upload CSV or TXT", type=['csv', 'txt'])
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            urls = [u.strip() for u in content.split('\n') if is_valid_tiktok(u)]

    # Actions
    col1, col2 = st.columns([1, 4])
    with col1:
        start_btn = st.button("Process URLs", type="primary", disabled=len(urls) == 0)
    with col2:
        st.write(f"**{len(urls)}** valid URLs detected.")

    if start_btn:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.empty()

        total_urls = len(urls)
        
        for idx, url in enumerate(urls):
            # Batch Cooldown
            if idx > 0 and idx % batch_size == 0:
                status_text.warning(f"Batch limit reached. Cooling down for {cooldown}s...")
                time.sleep(cooldown)

            status_text.text(f"Processing {idx+1}/{total_urls}...")
            
            # Process with retry logic
            res = process_url_with_retry(url, max_retries, jitter_range, use_proxies)
            results.append(res)
            
            progress_bar.progress((idx + 1) / total_urls)
            
            # Update live table
            df = pd.DataFrame(results)
            results_container.dataframe(df, use_container_width=True)

        status_text.success("Processing Complete!")
        
        # Summary & Download
        success_count = len([r for r in results if "Success" in r["Status"]])
        st.write(f"Summary: {success_count} success, {total_urls - success_count} failed.")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results CSV", csv, "tiktok_audio_data.csv", "text/csv", use_container_width=True)

if __name__ == "__main__":
    run_app()