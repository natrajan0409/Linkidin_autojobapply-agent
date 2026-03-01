from src.utils.browser_manager import BrowserManager
import time

def check_linkedin_login():
    """
    Opens LinkedIn and checks if the user is already logged in. 
    If not, it waits for the user to log in manually to save the session.
    """
    bm = BrowserManager()
    page = bm.start()
    
    print("Opening LinkedIn to check session...")
    page.goto("https://www.linkedin.com/feed/", wait_until="networkidle")
    
    # Check for login indicators (e.g., search bar or profile icon)
    # If we are on the login page or feed isn't loading, we might not be logged in
    try:
        # Wait for either the feed or the login button
        page.wait_for_selector(".global-nav__me-boundary, .nav__button-secondary", timeout=10000)
        
        if page.query_selector(".global-nav__me-boundary"):
            print("Successfully detected persistent session!")
            return True
        else:
            print("\n!!! ACTION REQUIRED !!!")
            print("LinkedIn session not found. Please log in manually in the browser window that just opened.")
            print("Once you are logged in and seeing your feed, I will save the session.")
            
            # Wait for user to log in manually
            page.wait_for_selector(".global-nav__me-boundary", timeout=300000) # 5 minute timeout
            print("Login detected! Session saved.")
            return True
                
    except Exception as e:
        print(f"Error checking session: {e}")
        return False
    finally:
        # Give some time for cookies to save before closing
        time.sleep(5)
        bm.stop()

if __name__ == "__main__":
    check_linkedin_login()
