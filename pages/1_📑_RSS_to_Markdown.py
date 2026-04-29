import streamlit as st

st.title("📑 RSS to Markdown Converter")

# Input field for the raw text/xml
raw_input = st.text_area("Paste your RSS/XML content here:", height=300)

if st.button("Convert to Markdown"):
    if raw_input:
        # This is where your existing logic goes
        # transformed_text = my_conversion_function(raw_input)
        transformed_text = f"### Processed Markdown\n\n{raw_input}" # Placeholder
        
        st.subheader("Result")
        st.code(transformed_text, language='markdown')
        
        st.download_button(
            label="Download .md File",
            data=transformed_text,
            file_name="converted_feed.md",
            mime="text/markdown"
        )
    else:
        st.warning("Please paste some content first!")