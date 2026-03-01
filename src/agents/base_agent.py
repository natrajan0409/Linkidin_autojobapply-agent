from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, agent_name, model_name=None):
        self.agent_name = agent_name
        self.api_key = os.getenv("GOOGLE_API_KEY")
        # Use a robust default if none provided
        self.model_name = model_name or "gemini-1.5-flash"
        
        if not self.api_key:
            raise ValueError(f"GOOGLE_API_KEY not found for {self.agent_name}")
        
        self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def list_available_models(api_key):
        """Lists available Gemini models for the given API key."""
        try:
            client = genai.Client(api_key=api_key)
            models = []
            for m in client.models.list():
                try:
                    # Extremely defensive check
                    name = getattr(m, 'name', str(m))
                    name = name.replace('models/', '')
                    
                    # If we can't check methods, just include it
                    models.append(name)
                except:
                    continue
            
            # Filter for likely text models if we have many
            if len(models) > 5:
                # Include anything with 'gemini' in the name
                models = [m for m in models if 'gemini' in m.lower()]
            
            return sorted(set(models)) if models else ["gemini-1.5-flash", "gemini-1.5-pro"]
        except Exception as e:
            return [f"Error fetching models: {str(e)}"]

    def generate_response(self, prompt, role_description=""):
        try:
            full_prompt = f"{role_description}\n\nTask: {prompt}"
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

class ResumeAgent(BaseAgent):
    def __init__(self, model_name=None):
        super().__init__("ResumeAgent", model_name=model_name)

    def generate_resume(self, job_description):
        prompt = f" edit the resume for the following job description: {job_description}"
        return self.generate_response(prompt, "You are a resume editing assistant.")
    
    def generate_cover_letter(self, job_description):
        prompt = f"Generate a cover letter for the following job description: {job_description}"
        return self.generate_response(prompt, "You are a cover letter writing assistant.")

    def generate_linkedin_summary(self, job_description):
        prompt = f"Generate a LinkedIn summary for the following job description: {job_description}"
        return self.generate_response(prompt, "You are a LinkedIn summary writing assistant.")

    def generate_linkedin_headline(self, job_description):
        prompt = f"Generate a LinkedIn headline for the following job description: {job_description}"
        return self.generate_response(prompt, "You are a LinkedIn headline writing assistant.")
    
    def tailor_resume(self, original_resume, job_description):
        prompt = f"""
        Original Resume: {original_resume}
        Target Job Description: {job_description}
        
        Please rewrite the 'Professional Summary' and 'Skills' sections of the resume to align perfectly with the job description. 
        Maintain the original experience but rephrase bullet points to highlight relevant technologies mentioned in the job post.
        Return the result in clean Markdown format.
        """
        return self.generate_response(prompt, "You are an expert career coach and resume writer.")

class SearchAgent(BaseAgent):
    def __init__(self, model_name=None):
        super().__init__("SearchAgent", model_name=model_name)

    def find_jobs(self, job_title, location="Remote"):
        prompt = f"Generate 5 variations of search terms for the job title '{job_title}' in {location} to maximize results on LinkedIn."
        return self.generate_response(prompt, "You are a lead recruitment researcher.")

class ApplyAgent(BaseAgent):
    def __init__(self, model_name=None):
        super().__init__("ApplyAgent", model_name=model_name)

    def prepare_application_data(self, job_details, user_profile):
        prompt = f"""
        Job Details: {job_details}
        User Profile: {user_profile}
        
        Extract the key requirements and determine if the user is a good fit. 
        If so, generate a concise 'Why me' statement for the application.
        """
        return self.generate_response(prompt, "You are an expert job application strategist.")

class JobApplicationWorkflow:
    def __init__(self, model_name=None):
        self.resume_agent = ResumeAgent(model_name=model_name)
        self.search_agent = SearchAgent(model_name=model_name)
        self.apply_agent = ApplyAgent(model_name=model_name)

    def run(self, job_title, original_resume, location="Remote"):
        search_params = self.search_agent.find_jobs(job_title, location)
        tailored_resume = self.resume_agent.tailor_resume(original_resume, job_title)
        app_strategy = self.apply_agent.prepare_application_data(job_title, original_resume)

        return {
            "search_strategy": search_params,
            "tailored_resume": tailored_resume,
            "application_strategy": app_strategy
        }
