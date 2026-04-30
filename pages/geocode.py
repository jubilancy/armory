import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import io

def run_app():
    st.set_page_config(page_title="Batch Geocoder", page_icon="📍")
    st.title("📍 Batch Geocoder")
    st.markdown("Convert place names or addresses into coordinates and view them on a map.")

    # Sidebar Settings
    st.sidebar.header("⚙️ Geocoder Settings")
    user_agent = st.sidebar.text_input("User Agent", value="armory_geocoder_v1")
    min_delay = st.sidebar.slider("Delay between requests (s)", 1.0, 5.0, 1.1)
    
    # Input Method
    input_method = st.radio("Input Method", ["Paste Names", "Upload CSV"], horizontal=True)
    places = []

    if input_method == "Paste Names":
        raw_input = st.text_area("Enter place names (one per line):", height=200, placeholder="Eiffel Tower\nStatue of Liberty\nTokyo Tower")
        if raw_input:
            places = [p.strip() for p in raw_input.split('\n') if p.strip()]
    else:
        uploaded_file = st.file_uploader("Upload CSV (must have a 'name' column)", type=['csv'])
        if uploaded_file:
            try:
                df_in = pd.read_csv(uploaded_file)
                if 'name' in df_in.columns:
                    places = df_in['name'].dropna().tolist()
                else:
                    st.error("CSV must contain a column named 'name'.")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

    if places:
        st.info(f"Found {len(places)} locations to geocode.")
        
        if st.button("Start Geocoding", type="primary", use_container_width=True):
            # Initialize Geocoder
            geolocator = Nominatim(user_agent=user_agent)
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=min_delay)
            
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, name in enumerate(places):
                status_text.text(f"Geocoding {idx+1}/{len(places)}: {name}")
                
                try:
                    location = geocode(name)
                    if location:
                        results.append({
                            "name": name,
                            "address": location.address,
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "status": "Success"
                        })
                    else:
                        results.append({"name": name, "status": "Not Found"})
                except Exception as e:
                    results.append({"name": name, "status": f"Error: {e}"})

                progress_bar.progress((idx + 1) / len(places))
            
            status_text.empty()
            
            if results:
                df_results = pd.DataFrame(results)
                st.success(f"Geocoding complete! {len(df_results[df_results['status'] == 'Success'])} found.")
                
                # Show Map for successful results
                map_data = df_results[df_results['status'] == 'Success'][['latitude', 'longitude']].dropna()
                if not map_data.empty:
                    st.subheader("🗺️ Map Visualization")
                    st.map(map_data)
                else:
                    st.warning("No coordinates found to display on map.")

                # Show Table
                st.subheader("📊 Data Table")
                st.dataframe(df_results, use_container_width=True)

                # Export
                csv = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Geocoded Results",
                    data=csv,
                    file_name="geocoded_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )

if __name__ == "__main__":
    run_app()