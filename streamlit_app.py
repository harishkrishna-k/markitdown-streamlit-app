import streamlit as st
import io
import os
import sys

# Add local package to path as a fallback
current_dir = os.path.dirname(os.path.abspath(__file__))
package_path = os.path.join(current_dir, "packages", "markitdown", "src")
if os.path.exists(package_path) and package_path not in sys.path:
    sys.path.insert(0, package_path)

from markitdown import MarkItDown, StreamInfo
st.set_page_config(
    page_title="MarkItDown Converter",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for better aesthetics and hiding menu
st.markdown("""
<style>
    /* Hide the hamburger menu and header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📝 MarkItDown")
    st.subheader("Convert any document or webpage to Markdown")
    
    st.info("Supported: PDF, Word, Excel, PowerPoint, HTML, ZIP, Images, Audio, and Web URLs.")
    
    tab1, tab2 = st.tabs(["📁 Upload File", "🌐 Convert URL"])
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Upload a file to convert", 
            type=None,
            accept_multiple_files=False
        )

        if uploaded_file is not None:
            if st.button("Convert File"):
                with st.spinner("🔄 Converting file..."):
                    try:
                        md = MarkItDown()
                        uploaded_file.seek(0)
                        
                        stream_info = StreamInfo(
                            filename=uploaded_file.name,
                            extension=os.path.splitext(uploaded_file.name)[1]
                        )
                        
                        result = md.convert(uploaded_file, stream_info=stream_info)
                        display_result(result, uploaded_file.name)
                        
                    except Exception as e:
                        st.error(f"❌ An error occurred during conversion: {str(e)}")
                        st.exception(e)

    with tab2:
        url = st.text_input("Enter a URL to convert (e.g., https://example.com)")
        if st.button("Convert URL"):
            if url:
                with st.spinner("🔄 Fetching and converting URL..."):
                    try:
                        md = MarkItDown()
                        result = md.convert(url)
                        
                        # Generate a filename from the URL or title
                        filename = "webpage.md"
                        if result.title:
                            filename = f"{result.title}.md"
                        
                        display_result(result, filename)
                        
                    except Exception as e:
                        st.error(f"❌ An error occurred during conversion: {str(e)}")
                        st.exception(e)
            else:
                st.warning("Please enter a valid URL.")

def display_result(result, original_filename):
    st.success("✅ Conversion successful!")
    
    # Display preview
    with st.expander("Preview Markdown Content"):
        st.markdown(result.text_content)
    
    # Prepare for download
    output_filename = os.path.splitext(original_filename)[0] + ".md"
    
    st.download_button(
        label="📥 Download Markdown File",
        data=result.text_content,
        file_name=output_filename,
        mime="text/markdown",
    )

    st.markdown("---")
    st.caption("Powered by [MarkItDown](https://github.com/microsoft/markitdown)")

if __name__ == "__main__":
    main()
