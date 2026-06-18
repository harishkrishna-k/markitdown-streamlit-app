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

# Modern UI CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    .main > div {
        padding-top: 1.5rem;
    }

    /* Card containers */
    div.stTabs [data-baseweb="tab-panel"] {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 1.8rem 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.06);
        border: 1px solid rgba(255,255,255,0.7);
    }

    div.stTabs [role="tablist"] {
        gap: 0.5rem;
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(8px);
        padding: 0.4rem;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.6);
        margin-bottom: 1.5rem;
    }

    div.stTabs [role="tab"] {
        border-radius: 10px;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }

    div.stTabs [role="tab"][aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        border: none;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,123,255,0.2);
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0,123,255,0.3);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    .stDownloadButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
        border: 1px solid #e0e0e0;
        transition: all 0.2s ease;
    }

    .stDownloadButton>button:hover {
        border-color: #007bff;
        color: #007bff;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.5);
        border: 2px dashed #c0c0c0;
        border-radius: 14px;
        padding: 1rem;
        transition: all 0.2s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #007bff;
        background: rgba(255,255,255,0.8);
    }

    [data-testid="stFileUploaderPagination"] small {
        visibility: hidden;
    }

    [data-testid="stFileUploaderPagination"]::after {
        content: "Max file size: 200 MB";
        font-size: 0.8rem;
        color: #888;
        display: block;
        margin-top: -1.2rem;
    }

    /* Text input */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 0.6rem 1rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        background: rgba(255,255,255,0.7);
    }

    .stTextInput>div>div>input:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
    }

    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 10px;
        font-weight: 500;
        background: rgba(255,255,255,0.5);
        transition: all 0.2s ease;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(255,255,255,0.8);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255,255,255,0.5);
    }

    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-weight: 600;
        font-size: 1rem;
        color: #333;
    }

    /* Success/info/warning alerts */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* Spinner */
    .stSpinner>div>div {
        border-color: #007bff transparent transparent transparent;
    }

    /* Text area (cookies) */
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        background: rgba(255,255,255,0.7);
    }

    .stTextArea textarea:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
    }

    /* Caption */
    .stCaption {
        color: #888;
        font-size: 0.85rem;
    }

    hr {
        margin: 1.2rem 0;
        border-color: rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialise session state for persistence across reruns
    if "cookies_text" not in st.session_state:
        st.session_state.cookies_text = ""
    if "conversion_result" not in st.session_state:
        st.session_state.conversion_result = None

    # --- Header Section ---
    st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 2.5rem;">
            <div style="font-size: 3.2rem; margin-bottom: 0.3rem;">📝</div>
            <h1 style="font-size: 2.8rem; font-weight: 800; margin: 0; letter-spacing: -0.03em; background: linear-gradient(135deg, #1a1a2e, #007bff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">MarkItDown</h1>
            <p style="font-size: 1.1rem; color: #888; margin-top: 0.5rem; font-weight: 400;">Turn documents & webpages into clean Markdown, instantly.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Sidebar ---
    with st.sidebar:
        st.markdown("""
            <div style="padding: 0.5rem 0 1rem; border-bottom: 1px solid #eee; margin-bottom: 1.2rem;">
                <h3 style="margin: 0; font-weight: 700; font-size: 1.1rem;">⚙️ Settings</h3>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="font-size: 0.85rem; font-weight: 600; color: #555; margin-bottom: 0.5rem;">Supported Formats</div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.85rem; line-height: 1.8;">
            📄 PDF, Word, PPT · 📊 Excel, CSV · 🌐 HTML, Articles · 📦 ZIP · 🎵 MP3, WAV
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 1.2rem 0; border-color: #eee;'>", unsafe_allow_html=True)

        with st.expander("🔑 Authentication", expanded=False):
            st.caption("Paste cookies if a website blocks conversion.")
            ui_cookies = st.text_area(
                "Cookies (Netscape format)",
                help="Paste the content of your cookies.txt here.",
                height=130,
                key="cookies_text"
            )
            if ui_cookies:
                st.success("Session cookies loaded")
                if st.button("Clear Session"):
                    st.session_state.cookies_text = ""
                    st.rerun()

    # --- Main Interface ---
    tab1, tab2 = st.tabs(["📁 Upload Document", "🌐 Convert Webpage"])
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=None,
            accept_multiple_files=False,
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            st.markdown("<hr style='margin: 1rem 0; border-color: #eee;'>", unsafe_allow_html=True)
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; height: 100%;">
                        <span style="font-size: 1.2rem;">📎</span>
                        <span style="font-weight: 500; color: #333;">{uploaded_file.name}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🚀 Convert Now", type="primary", key="btn_file", use_container_width=True):
                    process_conversion(uploaded_file, ui_cookies)

    with tab2:
        url_input = st.text_input(
            "URL",
            placeholder="https://example.com/article",
            label_visibility="collapsed"
        )

        if st.button("🔍 Fetch and Convert", type="primary", key="btn_url", use_container_width=True):
            if url_input:
                unsupported_domains = ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com", "twitter.com", "x.com"]
                if any(domain in url_input.lower() for domain in unsupported_domains):
                    st.error("🚫 **Unsupported Link:** Media-heavy platforms (YouTube, Instagram, etc.) are not supported for scraping. Please use a text-based article or blog post URL.")
                else:
                    process_url(url_input, ui_cookies)
            else:
                st.warning("Please enter a URL first!")

    # Display persisted conversion result across reruns
    result_entry = st.session_state.conversion_result
    if result_entry:
        result, original_filename = result_entry
        display_result(result, original_filename)

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
            st.session_state.conversion_result = (result, uploaded_file.name)
            
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
            st.session_state.conversion_result = (result, "webpage.md")
            
        except Exception as e:
            st.error(f"❌ URL conversion failed: {str(e)}")

def display_result(result, original_filename):
    st.markdown("""
        <div style="margin: 1.5rem 0 0.5rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, #d4edda, #c3e6cb); border-radius: 12px; padding: 0.8rem 1.2rem;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span style="font-size: 1.3rem;">✅</span>
                    <span style="font-weight: 600; color: #155724;">Conversion complete!</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    output_filename = os.path.splitext(original_filename)[0] + ".md"

    col1, col2 = st.columns([2, 1])
    with col1:
        with st.expander("🔍 Preview Markdown", expanded=True):
            st.markdown(
                result.text_content,
                unsafe_allow_html=False
            )
    with col2:
        st.download_button(
            label="📥 Download .md",
            data=result.text_content,
            file_name=output_filename,
            mime="text/markdown",
            use_container_width=True,
            type="primary"
        )
        if st.button("✕ Dismiss", key="dismiss_result", use_container_width=True):
            st.session_state.conversion_result = None
            st.rerun()

    st.markdown("""
        <div style="text-align: center; padding: 2rem 0 0.5rem;">
            <span style="font-size: 0.8rem; color: #aaa;">Powered by <a href="https://github.com/microsoft/markitdown" style="color: #007bff; text-decoration: none;">MarkItDown</a></span>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
