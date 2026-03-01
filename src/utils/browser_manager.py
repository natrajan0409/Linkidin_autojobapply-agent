import os
import time
import asyncio
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from dotenv import load_dotenv

# Force Proactor Loop Policy for Windows/Python 3.14 compatibility
if sys.platform == 'win32':
    try:
        # Check if policy is already set to avoid deprecation warnings if possible
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except:
        pass

load_dotenv()

class BrowserManager:
    """
    Manages a persistent Playwright browser session to maintain LinkedIn login 
    and avoid bot detection.
    """
    def __init__(self, user_data_dir=None):
        # Use stable local directory for persistent sessions
        if user_data_dir is None:
            self.user_data_dir = str(Path("data/browser_session").absolute())
        else:
            self.user_data_dir = str(Path(user_data_dir).absolute())
            
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None
        self.headless = False
        
        # Ensure user data dir exists
        os.makedirs(self.user_data_dir, exist_ok=True)

    def start(self):
        """Launches the persistent browser context."""
        try:
            # Force a new loop if we are in a thread (like Streamlit)
            if sys.platform == 'win32':
                try:
                    asyncio.get_event_loop()
                except RuntimeError:
                    asyncio.set_event_loop(asyncio.new_event_loop())

            if not self.pw:
                self.pw = sync_playwright().start()
                
            self.context = self.pw.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                no_viewport=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )
            
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            
            # Use the class-based stealth application (more robust across versions)
            Stealth().apply_stealth_sync(self.page)
            
            return self.page
            
        except Exception as e:
            # Clean up if launch fails
            self.stop()
            raise Exception(f"Failed to start browser: {str(e)}")

    def navigate(self, url):
        """Safely navigates to a URL with human-like delays."""
        if not self.page:
            self.start()
        
        self.page.goto(url, wait_until="networkidle")
        time.sleep(2)
        return self.page

    def stop(self):
        """Stops the browser and playwright."""
        try:
            if self.context:
                self.context.close()
            if self.pw:
                self.pw.stop()
        except:
            pass
        finally:
            self.context = None
            self.pw = None
            self.page = None

    def get_page(self):
        """Returns the primary page."""
        return self.page

    def get_active_page(self):
        """Returns the most recently opened page/tab."""
        if self.context and self.context.pages:
            return self.context.pages[-1]
        return self.page
