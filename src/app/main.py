import streamlit as st
import os
import sys
import asyncio

# Fix for asyncio NotImplementedError on Windows with newer Python versions
if sys.platform == 'win32':
    try:
        # Force the policy BEFORE anything else
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

# Add src to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.agents.base_agent import SearchAgent, ResumeAgent
from src.utils.pdf_parser import get_resume_content
from src.utils.browser_manager import BrowserManager
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="LinkedIn Auto-Apply Agent", page_icon="🤖", layout="wide")

st.title("🤖 LinkedIn Auto-Apply Agent")

# Session state initialization
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "search_strategy" not in st.session_state:
    st.session_state.search_strategy = None
if "linkedin_logged_in" not in st.session_state:
    st.session_state.linkedin_logged_in = False

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Google Gemini API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
    
    st.subheader("Model Settings")
    
    # Initialize dynamic model list
    if "available_models" not in st.session_state:
        st.session_state.available_models = ["gemini-1.5-flash", "gemini-1.5-pro"]
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        # Refresh model list if key is provided and list is just defaults
        if st.sidebar.button("Fetch Available Models") or len(st.session_state.available_models) <= 2:
            from src.agents.base_agent import BaseAgent
            with st.spinner("Fetching available models..."):
                fetched_models = BaseAgent.list_available_models(api_key)
                if fetched_models:
                    st.session_state.available_models = fetched_models
        
    model_name = st.selectbox(
        "Select Gemini Model",
        st.session_state.available_models,
        index=0,
        help="The list is fetched dynamically from your API account."
    )
    
    if api_key:
        st.success("API Key active!")
    
    st.divider()
    st.header("LinkedIn Session")
    
    # Persistent browser manager in session state to stay open during login
    if "browser_manager" not in st.session_state:
        st.session_state.browser_manager = None

    if not st.session_state.linkedin_logged_in:
        st.warning("Not logged in to LinkedIn")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Login"):
                try:
                    with st.spinner("Launching browser..."):
                        st.session_state.browser_manager = BrowserManager()
                        page = st.session_state.browser_manager.start()
                        page.goto("https://www.linkedin.com/login", wait_until="networkidle")
                        st.info("Browser opened. Please log in manually in the new window.")
                except Exception as e:
                    st.error(f"Launch error: {e}")
        
        with col2:
            if st.button("Confirm Login") and st.session_state.browser_manager:
                try:
                    # Check the most active page (in case of redirects)
                    page = st.session_state.browser_manager.get_active_page()
                    current_url = page.url
                    
                    # Log for debugging
                    st.write(f"Checking page: {current_url}")
                    
                    # 1. Broad URL check (if we are on feed or search, we are logged in)
                    is_logged_in = "linkedin.com/feed" in current_url or "linkedin.com/search" in current_url
                    
                    # 2. Selector check (Me icon or Nav bar)
                    if not is_logged_in:
                        selectors = [".global-nav__me-boundary", "#global-nav", ".nav-main__item--me"]
                        for selector in selectors:
                            try:
                                if page.query_selector(selector):
                                    is_logged_in = True
                                    break
                            except:
                                continue
                    
                    if is_logged_in:
                        st.session_state.linkedin_logged_in = True
                        st.session_state.browser_manager.stop()
                        st.session_state.browser_manager = None
                        st.success("Session saved and browser closed!")
                        st.rerun()
                    else:
                        st.error("Login not detected. Please ensure you have finished logging in and are on the LinkedIn home feed.")
                        if st.button("Retry Detection"):
                            st.rerun()
                except Exception as e:
                    st.error(f"Detection failed: {e}")
    else:
        st.success("LinkedIn Session Active ✅")
        if st.button("Logout / Clear Session"):
            st.session_state.linkedin_logged_in = False
            # Optional: Clear data directory manually if needed
            st.rerun()

tab1, tab2 = st.tabs(["User Profile", "Job Search & Apply"])

with tab1:
    st.header("Profile Information")
    job_title = st.text_input("Target Job Title", placeholder="e.g. Senior Software Engineer")
    skills = st.text_area("Key Skills", placeholder="e.g. Python, PyTorch, CUDA, React")
    experience = st.text_area("Work Experience", placeholder="Describe your background briefly...")
    
    uploaded_file = st.file_uploader("Upload Current Resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        # Save to data/resumes/
        resume_path = os.path.join("data", "resumes", uploaded_file.name)
        os.makedirs(os.path.dirname(resume_path), exist_ok=True)
        with open(resume_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract text
        try:
            st.session_state.resume_text = get_resume_content(resume_path)
            st.success(f"Resume '{uploaded_file.name}' uploaded and parsed!")
        except Exception as e:
            st.error(f"Error parsing resume: {e}")
    
    if st.button("Save Profile"):
        st.info("Profile data saved in session!")

with tab2:
    st.header("Job Search & Automation")
    st.write("Search for jobs and apply automatically using tailored resumes.")
    
    search_query = st.text_input("Search Keyword", value=job_title if job_title else "")
    location = st.text_input("Location", value="Remote")
    
    if st.button("Start Search"):
        if not api_key:
            st.error("Please provide a Gemini API Key in the sidebar.")
        else:
            with st.spinner(f"Generating search strategy for '{search_query}'..."):
                try:
                    search_agent = SearchAgent(model_name=model_name)
                    st.session_state.search_strategy = search_agent.find_jobs(search_query, location)
                    st.success("Search strategy generated!")
                except Exception as e:
                    st.error(f"Search failed: {e}")

    if st.session_state.search_strategy:
        st.subheader("Targeted Search Terms")
        st.markdown(st.session_state.search_strategy)
        
        st.info("💡 Next Step: I will use these terms to browse LinkedIn via Playwright (Upcoming Feature).")
