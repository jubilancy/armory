# /// script
# dependencies = [
#     "streamlit",
#     "himalaya",
# ]
# ///

import streamlit as st
import json

# Safe import for Streamlit Cloud environments
try:
    import himalaya
    HIMALAYA_AVAILABLE = True
except ImportError:
    HIMALAYA_AVAILABLE = False

def run_himalaya_tool():
    st.title("📂 Himalaya: HTML to JSON")
    
    if not HIMALAYA_AVAILABLE:
        st.error("### 🛠️ Library Missing")
        st.warning("""
        **Action Required:** Streamlit Cloud cannot find the `himalaya` library. 
        Please add `himalaya` to your `requirements.txt` file in the root of your repository.
        """)
        st.info("Once you update `requirements.txt` and push to GitHub, Streamlit will rebuild and this tool will work.")
        return

    st.markdown("""
    Convert raw HTML into a structured JSON format instantly. 
    This tool uses the [Himalaya](https://github.com/andrejewski/himalaya) parser.
    """)

    # 1. Input: Text area for HTML content
    html_input = st.text_area(
        "Paste your HTML here:",
        placeholder="<html><body><h1>Hello World</h1></body></html>",
        height=300
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        # 2. Trigger: Button to start conversion
        convert_pressed = st.button("Convert to JSON", use_container_width=True, type="primary")

    if convert_pressed:
        if not html_input.strip():
            st.error("Please paste some HTML content first.")
        else:
            try:
                # Processing logic using himalaya
                json_data = himalaya.parse(html_input)
                json_string = json.dumps(json_data, indent=2)

                st.success("Conversion Successful!")
                
                # 3. Output: Display and Download
                st.subheader("Resulting JSON")
                st.code(json_string, language="json")

                st.download_button(
                    label="Download JSON File",
                    data=json_string,
                    file_name="converted_html.json",
                    mime="application/json",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"An error occurred during parsing: {e}")

if __name__ == "__main__":
    run_himalaya_tool()
