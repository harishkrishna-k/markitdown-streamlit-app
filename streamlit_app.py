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
    st.subheader("Convert documents to Markdown")
    
    # Restrict file types to PDF, Word, Excel, and PPT
    allowed_types = ["pdf", "docx", "xlsx", "xls", "pptx"]
    
    uploaded_file = st.file_uploader(
        "Upload a document (PDF, Word, Excel, or PowerPoint)", 
        type=allowed_types,
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        if st.button("Convert to Markdown"):
            with st.spinner("🔄 Converting..."):
                try:
                    md = MarkItDown()
                    
                    # MarkItDown.convert can take a file-like object (BinaryIO)
                    # We need to make sure we're at the beginning of the file
                    uploaded_file.seek(0)
                    
                    # Use StreamInfo for better format detection
                    from markitdown import StreamInfo
                    stream_info = StreamInfo(
                        filename=uploaded_file.name,
                        extension=os.path.splitext(uploaded_file.name)[1]
                    )
                    
                    result = md.convert(uploaded_file, stream_info=stream_info)
                    
                    st.success("✅ Conversion successful!")
                    
                    # Display preview
                    with st.expander("Preview Markdown Content"):
                        st.markdown(result.text_content)
                    
                    # Prepare for download
                    output_filename = os.path.splitext(uploaded_file.name)[0] + ".md"
                    
                    st.download_button(
                        label="📥 Download Markdown File",
                        data=result.text_content,
                        file_name=output_filename,
                        mime="text/markdown",
                    )
                    
                except Exception as e:
                    st.error(f"❌ An error occurred during conversion: {str(e)}")
                    st.exception(e)

    st.markdown("---")
    st.caption("Powered by [MarkItDown](https://github.com/microsoft/markitdown)")

if __name__ == "__main__":
    main()
