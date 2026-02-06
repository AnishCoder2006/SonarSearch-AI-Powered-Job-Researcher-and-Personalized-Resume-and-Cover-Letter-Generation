from crewai import Agent, Task, LLM
from langchain_google_genai import ChatGoogleGenerativeAI  # fallback
from utils.config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE
import json
import re

class ResumeCoverLetterAgent:
    def __init__(self):
        # Preferred: CrewAI LLM wrapper
        self.llm = LLM(
            model=GEMINI_MODEL,              # e.g. "gemini/gemini-1.5-flash" or "gemini/gemini-1.5-pro"
            api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
        )

        # Uncomment this fallback if you keep getting LiteLLM / messages validation errors
        # self.llm = ChatGoogleGenerativeAI(
        #     model=GEMINI_MODEL.replace("gemini/", "").replace("gemini-", ""),
        #     google_api_key=GEMINI_API_KEY,
        #     temperature=TEMPERATURE,
        #     max_output_tokens=4096,
        # )

        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        return Agent(
            role='Professional Resume and Cover Letter Writer',
            goal='Create tailored resumes and compelling cover letters that match specific job requirements and highlight candidate strengths',
            backstory="""You are a certified professional resume writer and career coach with 12+ years of experience 
            helping candidates land their dream jobs at top companies (including federal roles via USAJOBS). You have an exceptional ability to analyze 
            job requirements and candidate backgrounds to create perfectly matched application materials. 
            You're known for your persuasive writing style, attention to detail, and understanding of what 
            recruiters, hiring panels, and ATS systems look for in applications.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def _run_prompt(self, prompt: str, expected: str = "Valid JSON object") -> str:
        """Unified method to run prompt – tries multiple execution patterns"""
        try:
            # Preferred: simple kickoff with string
            result = self.agent.kickoff(prompt)
            return str(result)
        except Exception as kickoff_err:
            print(f"kickoff() failed: {kickoff_err}")
            try:
                # Fallback 1: Use Task.execute()
                task = Task(
                    description=prompt,
                    agent=self.agent,
                    expected_output=expected
                )
                result = task.execute()
                return str(result)
            except Exception as task_err:
                print(f"Task.execute() failed: {task_err}")
                # Fallback 2: Direct LLM call (most reliable with Gemini)
                try:
                    messages = [
                        {"role": "system", "content": self.agent.backstory + "\n\n" + self.agent.goal},
                        {"role": "user", "content": prompt}
                    ]
                    response = self.llm.invoke(messages)
                    return response.content if hasattr(response, 'content') else str(response)
                except Exception as llm_err:
                    raise RuntimeError(f"All execution methods failed.\n"
                                     f"kickoff: {kickoff_err}\n"
                                     f"Task: {task_err}\n"
                                     f"Direct LLM: {llm_err}")

    def customize_resume(self, resume_text: str, job_analysis: dict) -> dict:
        prompt = f"""
Create a tailored resume for the job '{job_analysis.get("job_title", "Unknown")}' 
at '{job_analysis.get("agency", "Unknown")}' (USAJOBS federal position).

JOB ANALYSIS SUMMARY:
{json.dumps(job_analysis, indent=2)}

ORIGINAL RESUME TEXT:
{resume_text}

Instructions:
1. Identify and prioritize skills/experiences that match job requirements.
2. Rephrase bullet points to emphasize relevance; use strong action verbs.
3. Incorporate exact keywords/phrases from the job analysis (especially qualification summary & duties).
4. Quantify achievements (%, $, numbers) wherever possible or reasonable.
5. Add a strong professional summary at the top targeted to this role.
6. Keep length similar to original; ensure ATS-friendly (standard sections, no fancy formatting).
7. Output clean, plain-text formatted resume.

Return ONLY valid JSON — no other text, no markdown, no explanations:
{{
    "customized_resume": "full resume text here (use \\n for line breaks)",
    "summary_of_changes": "detailed explanation of changes and why they help",
    "keywords_added": ["list", "of", "added keywords"],
    "ats_score_improvement": "estimated improvement (e.g. from 45% → 85%)",
    "recommended_further_improvements": ["suggestion 1", "suggestion 2"]
}}
"""

        try:
            raw_result = self._run_prompt(prompt, "Valid JSON object with customized resume")
            return self._parse_json_response(raw_result)
        except Exception as e:
            print(f"Error customizing resume: {e}")
            return {"error": str(e), "customized_resume": resume_text}

    def generate_cover_letter(self, resume_text: str, job_analysis: dict, candidate_bio: str = "") -> dict:
        prompt = f"""
Generate a professional federal-style cover letter for '{job_analysis.get("job_title", "Unknown")}' 
at '{job_analysis.get("agency", "Unknown")}'.

JOB ANALYSIS SUMMARY:
{json.dumps(job_analysis, indent=2)}

CANDIDATE RESUME:
{resume_text}

ADDITIONAL BIO (if any):
{candidate_bio or "None provided"}

Requirements:
- Address to 'Dear Hiring Manager' or appropriate panel if known.
- Strong opening: state position (include control/position ID if available) and why interested.
- 2–3 body paragraphs: match 2–3 key qualifications with specific examples from resume.
- Show enthusiasm for public service / agency mission.
- End with call to action and professional close.
- 350–450 words, concise, confident tone.

Return ONLY valid JSON — no other text, no markdown, no explanations:
{{
    "cover_letter": "full cover letter text (use \\n for paragraphs)",
    "cover_letter_approach": "brief strategy explanation",
    "key_points_highlighted": ["point 1", "point 2"],
    "tone_analysis": "tone description and rationale",
    "recommended_modifications": ["optional tweak 1", "..."]
}}
"""

        try:
            raw_result = self._run_prompt(prompt, "Valid JSON object with cover letter")
            return self._parse_json_response(raw_result)
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return {"error": str(e), "cover_letter": "Error occurred"}

    def _parse_json_response(self, result: str, default_key: str = "result") -> dict:
        try:
            # Clean up common wrappers
            result = result.strip()
            result = re.sub(r'^```json\s*|\s*```$', '', result, flags=re.IGNORECASE | re.DOTALL)
            result = result.strip()

            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                parsed['raw_response'] = result
                return parsed

            return {default_key: result, "raw_response": result, "note": "Response was not pure JSON"}
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return {"error": f"JSON parse failed: {str(e)}", "raw_response": result[:1500]}

    def analyze_resume_ats_compatibility(self, resume_text: str, keywords: list[str]) -> dict:
        if not keywords:
            return {
                "ats_score": 0,
                "ats_percentage": 0,
                "keywords_found": [],
                "keywords_missing": [],
                "suggestions": ["No keywords provided for analysis"]
            }

        ats_score = 0
        max_score = len(keywords) * 2
        resume_lower = resume_text.lower()
        keywords_found = []
        keywords_missing = []

        for k in keywords:
            k_lower = k.lower()
            if k_lower in resume_lower:
                ats_score += 2
                keywords_found.append(k)
            else:
                parts = k_lower.split()
                if len(parts) > 1 and all(part in resume_lower for part in parts):
                    ats_score += 1
                    keywords_found.append(f"{k} (partial match)")
                else:
                    keywords_missing.append(k)

        ats_percentage = (ats_score / max_score * 100) if max_score > 0 else 0

        suggestions = []
        if ats_percentage < 60:
            suggestions.append(f"Add the {len(keywords_missing)} missing keywords/phrases to significantly improve ATS pass rate.")
        if len(resume_text.split()) > 800:
            suggestions.append("Shorten resume to 1-2 pages for better ATS & human readability.")

        return {
            "ats_score": ats_score,
            "ats_percentage": round(ats_percentage, 1),
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing[:10],
            "suggestions": suggestions
        }