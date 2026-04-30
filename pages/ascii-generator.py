import streamlit as st
from pyfiglet import Figlet, FigletFont

# Page Configuration for a wide layout like the original tool
st.set_page_config(page_title="ASCII Armory", layout="wide")

st.title("🎨 FIGlet ASCII Generator")

# 1. THE DROPDOWN (Sidebar)
# Automatically retrieves all 360+ available fonts from the library
all_fonts = sorted(FigletFont.getFonts())

st.sidebar.header("Font Settings")
selected_font = st.sidebar.selectbox(
    "Choose a Font:", 
    all_fonts, 
    index=all_fonts.index("slant") if "slant" in all_fonts else 0
)

# 2. THE INPUT: Replaces standard input() with a browser text box
user_text = st.text_input("Type Something:", value="Armory")

# 3. THE GENERATOR Logic
if user_text:
    try:
        f = Figlet(font=selected_font)
        ascii_art = f.renderText(user_text)
        
        # 4. THE OUTPUT: Using st.code ensures perfect monospace spacing
        st.code(ascii_art, language=None)
        
        # DOWNLOAD OPTION: Replaces local file saving
        st.download_button(
            label="Download ASCII Art",
            data=ascii_art,
            file_name=f"{selected_font}_art.txt",
            mime="text/plain"
        )
    except Exception:
        st.error(f"Error rendering font '{selected_font}'.")