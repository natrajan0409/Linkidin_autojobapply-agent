# 🤖 LinkedIn Auto-Apply Agent

An AI-powered multi-agent system designed to automate job searching and application on LinkedIn. This tool uses **Google Gemini** for intelligent strategy generation and resume tailoring, and **Playwright** for seamless browser automation.

## 🚀 Features
- **Intelligent Search**: Generates optimized Boolean search strings based on your profile.
- **Resume Tailoring**: Automatically adjusts your resume for specific job descriptions (Upcoming).
- **Persistent Sessions**: Securely maintains your LinkedIn login session to avoid repeated logins.
- **Stealth Mode**: Uses advanced evasion techniques to minimize bot detection.
- **Streamlit Interface**: Clean, user-friendly dashboard for managing your job hunt.

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher (Tested on 3.14)
- Google Gemini API Key

### 2. Installation
Clone the repository and install dependencies:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Running the App
Start the Streamlit dashboard:
```powershell
streamlit run src/app/main.py
```

---

## 🔑 How to Use the LinkedIn Session
1. In the sidebar, click **"Start Login"**.
2. A browser window will open. **Log in manually** to LinkedIn.
3. Once you arrive at your LinkedIn Feed, return to the app and click **"Confirm Login"**.
4. Your session is now saved! You won't need to log in again for future sessions.

---

## 📂 Project Structure
- `src/app/main.py`: Main Streamlit application.
- `src/agents/`: Gemini-powered agents for search and tailoring.
- `src/utils/browser_manager.py`: Playwright management and stealth logic.
- `data/`: Local storage for resumes and sessions (Git-ignored).

---

## 🛡️ Disclaimer
This tool is for educational and personal use only. Please respect LinkedIn's Terms of Service regarding automation.
