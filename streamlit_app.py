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

def time_format(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f'{h:d}:{m:02d}:{s:02d}'
    return f'{m:d}:{s:02d}'

# Set page config
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
    # --- Header Section ---
    st.markdown("""
        <div style="text-align: center; padding-bottom: 2rem;">
            <h1 style="font-size: 3rem; margin-bottom: 0;">📝 MarkItDown</h1>
            <p style="font-size: 1.2rem; color: #666;">The simplest way to turn documents and webpages into Markdown</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Sidebar for Advanced Settings ---
    with st.sidebar:
        st.header("🔧 Settings")
        
        st.markdown("### Supported Formats")
        st.markdown("""
        - 📄 **Documents:** PDF, Word, PPT
        - 📊 **Data:** Excel, CSV
        - 🌐 **Web:** HTML, Articles
        - 📦 **Archives:** ZIP
        - 🎵 **Audio:** MP3, WAV
        """)

        st.markdown("---")
        with st.expander("🔑 Authentication (Optional)", expanded=False):
            st.caption("Paste cookies here if a website blocks the conversion.")
            ui_cookies = st.text_area(
                "Cookies (Netscape format)",
                help="Paste the content of your cookies.txt here.",
                height=150
            )
            if ui_cookies:
                st.success("Session cookies loaded")
                if st.button("Clear Session"):
                    st.rerun()

    # --- Main Interface ---
    tab1, tab2 = st.tabs(["📁 Upload Document", "🌐 Convert Webpage"])
    
    with tab1:
        st.markdown("### 📄 Upload your file")
        st.caption("Drag and drop any supported document to get started.")
        
        uploaded_file = st.file_uploader(
            "Choose a file", 
            type=None,
            accept_multiple_files=False,
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            st.markdown("---")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Ready to convert:** `{uploaded_file.name}`")
            with col2:
                if st.button("🚀 Convert Now", type="primary", key="btn_file", use_container_width=True):
                    process_conversion(uploaded_file, ui_cookies)

    with tab2:
        st.markdown("### 🌐 Enter a URL")
        st.caption("Paste a link to any webpage or article (social media/video links not supported).")
        
        url_input = st.text_input(
            "URL",
            placeholder="https://example.com/article",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button("🔍 Fetch and Convert", type="primary", key="btn_url", use_container_width=True):
            if url_input:
                # Check for unsupported media domains
                unsupported_domains = ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com", "twitter.com", "x.com"]
                if any(domain in url_input.lower() for domain in unsupported_domains):
                    st.error("🚫 **Unsupported Link:** Media-heavy platforms (YouTube, Instagram, etc.) are not supported for scraping. Please use a text-based article or blog post URL.")
                else:
                    process_url(url_input, ui_cookies)
            else:
                st.warning("Please enter a URL first!")

def process_conversion(uploaded_file, ui_cookies):
    with st.spinner("⏳ Converting document..."):
        try:
            import requests
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            })
            
            cookie_content = ui_cookies if ui_cookies else st.secrets.get("YOUTUBE_COOKIES")
            if cookie_content:
                try:
                    for line in cookie_content.split('\n'):
                        if not line.startswith('#') and line.strip():
                            parts = line.split('\t')
                            if len(parts) >= 7:
                                session.cookies.set(parts[5], parts[6], domain=parts[0], path=parts[2])
                except: pass
            
            md = MarkItDown(requests_session=session)
            uploaded_file.seek(0)
            stream_info = StreamInfo(
                filename=uploaded_file.name,
                extension=os.path.splitext(uploaded_file.name)[1]
            )
            
            result = md.convert(uploaded_file, stream_info=stream_info)
            display_result(result, uploaded_file.name)
            
        except Exception as e:
            st.error(f"❌ Conversion failed: {str(e)}")

def process_url(url, ui_cookies):
    with st.spinner("🌐 Fetching content..."):
        try:
            import requests
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            })
            
            cookie_content = ui_cookies if ui_cookies else st.secrets.get("YOUTUBE_COOKIES")
            if cookie_content:
                try:
                    for line in cookie_content.split('\n'):
                        if not line.startswith('#') and line.strip():
                            parts = line.split('\t')
                            if len(parts) >= 7:
                                session.cookies.set(parts[5], parts[6], domain=parts[0], path=parts[2])
                except: pass
            
            md = MarkItDown(requests_session=session)
            stream_info = StreamInfo(url=url)
            result = md.convert(url, stream_info=stream_info)
            
            display_result(result, "webpage.md")
            
        except Exception as e:
            st.error(f"❌ URL conversion failed: {str(e)}")

def display_result(result, original_filename):
    st.markdown("---")
    st.balloons()
    st.success("✅ **Conversion complete!**")
    
    output_filename = os.path.splitext(original_filename)[0] + ".md"
    
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.expander("🔍 Preview Markdown", expanded=True):
            st.markdown(result.text_content)
    with col2:
        st.download_button(
            label="📥 Download .md File",
            data=result.text_content,
            file_name=output_filename,
            mime="text/markdown",
            use_container_width=True,
            type="primary"
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("Powered by [MarkItDown](https://github.com/microsoft/markitdown)")

if __name__ == "__main__":
    main()
