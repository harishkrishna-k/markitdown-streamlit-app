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
        st.header("🔧 Settings & Auth")
        with st.expander("🔑 YouTube Authentication", expanded=False):
            st.caption("Use this if you encounter 'Too Many Requests' errors on YouTube.")
            ui_cookies = st.text_area(
                "Paste Cookies.txt content",
                help="Netscape format cookies from YouTube.",
                height=150
            )
            if ui_cookies:
                st.success("Session cookies active")
                if st.button("Reset Session"):
                    st.rerun()
            
            st.markdown("---")
            st.markdown("**How to get cookies?**")
            st.markdown("1. Install [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/ccmclkhjbdinkhpdeadmjeidkhobhcmo)")
            st.markdown("2. Export from YouTube.com and paste here.")

        st.markdown("---")
        st.markdown("### Supported Formats")
        st.markdown("""
        - 📄 **Documents:** PDF, Word, PPT
        - 📊 **Data:** Excel, CSV
        - 🌐 **Web:** HTML, URLs
        - 📦 **Archives:** ZIP
        - 🎵 **Media:** MP3, WAV (Transcription)
        """)

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
                if st.button("🚀 Convert Now", type="primary", use_container_width=True):
                    process_conversion(uploaded_file, ui_cookies)

    with tab2:
        st.markdown("### 🌐 Enter a URL")
        st.caption("Paste a link to a blog post, article, or YouTube video.")
        
        url_input = st.text_input(
            "URL",
            placeholder="https://example.com/article",
            label_visibility="collapsed"
        )
        
        # Example buttons
        cols = st.columns([1, 1, 1, 2])
        with cols[0]:
            if st.button("💡 Wiki Example"):
                url_input = "https://en.wikipedia.org/wiki/Markdown"
        with cols[1]:
            if st.button("🎥 YouTube Example"):
                url_input = "https://www.youtube.com/watch?v=UkzKW1jsWqk"
        
        st.markdown("---")
        if st.button("🔍 Fetch and Convert", type="primary", use_container_width=True):
            if url_input:
                process_url(url_input, ui_cookies)
            else:
                st.warning("Please enter a URL first!")

def process_conversion(uploaded_file, ui_cookies):
    with st.spinner("⏳ Analyzing and converting your document..."):
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
    with st.spinner("🌐 Fetching webpage content..."):
        try:
            import requests
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            })
            
            cookies_path = None
            cookie_content = ui_cookies if ui_cookies else st.secrets.get("YOUTUBE_COOKIES")
            if cookie_content:
                with open("temp_cookies.txt", "w") as f:
                    f.write(cookie_content)
                cookies_path = "temp_cookies.txt"
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
            
            # YouTube recovery
            if "youtube.com/watch" in url or "youtu.be/" in url:
                if "AboutPressCopyright" in result.text_content or result.text_content.strip() == "YouTube":
                    result.text_content = "# YouTube Video\n"
                
                if "### Transcript" not in result.text_content:
                    try:
                        from youtube_transcript_api import YouTubeTranscriptApi
                        from urllib.parse import urlparse, parse_qs
                        video_id = None
                        if "youtu.be/" in url:
                            video_id = url.split("/")[-1].split("?")[0]
                        else:
                            parsed_url = urlparse(url)
                            params = parse_qs(parsed_url.query)
                            if "v" in params: video_id = params["v"][0]
                        
                        if video_id:
                            if cookies_path:
                                transcript = YouTubeTranscriptApi.get_transcript(video_id, cookies=cookies_path)
                            else:
                                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            
                            transcript_text = "\n".join([f"[{time_format(t['start'])}] {t['text']}" for t in transcript])
                            if result.text_content.strip() == "# YouTube Video":
                                 result.text_content += f"\n(Metadata blocked by YouTube, but transcript was recovered.)"
                            result.text_content += f"\n\n### Transcript\n{transcript_text}"
                    except Exception as yt_err:
                        if "429" in str(yt_err):
                            st.error("⚠️ YouTube is rate-limiting this request.")
                            st.info("💡 **Fix:** Paste your YouTube cookies into the sidebar Settings.")
                        else:
                            st.warning(f"Transcript note: {str(yt_err)}")
            
            filename = "webpage.md"
            if result.title and result.title != "YouTube":
                filename = f"{result.title}.md"
            elif "youtube.com" in url or "youtu.be" in url:
                filename = "youtube_video.md"
            
            display_result(result, filename)
            
        except Exception as e:
            st.error(f"❌ URL conversion failed: {str(e)}")

def display_result(result, original_filename):
    st.markdown("---")
    st.balloons()
    st.success("✅ **Great success!** Your file is ready.")
    
    output_filename = os.path.splitext(original_filename)[0] + ".md"
    
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.expander("🔍 Preview Markdown"):
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

