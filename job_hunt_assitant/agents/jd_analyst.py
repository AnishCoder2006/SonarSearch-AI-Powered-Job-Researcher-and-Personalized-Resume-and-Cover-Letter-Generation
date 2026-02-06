from crewai import Agent, Task, LLM
from utils.config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE
import json
import re
from typing import Dict, Any

class JobDescriptionAnalyst:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in config")

       
        self.llm = LLM(
            model=GEMINI_MODEL,               
            api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
            
        )

        self.agent = self.create_agent()

    def create_agent(self) -> Agent:
        return Agent(
            role='Senior Job Description Analyst',
            goal='Extract structured requirements and insights from job postings',
            backstory="""Expert HR professional with 12+ years analyzing federal and private sector job descriptions.
            Specialized in identifying must-have vs nice-to-have criteria, ATS keywords, and realistic application strategies.
            You excel at USAJOBS federal postings, understanding qualification summaries, KSAs, and how to match civilian experience.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def analyze_job_description(self, job_description: str, job_title: str, agency: str) -> Dict:
     try:
        print(f"[ANALYZER] Starting: {job_title} @ {agency}")

        prompt = f"""You are analyzing this job posting:

JOB TITLE: {job_title}
AGENCY: {agency}

FULL JOB DESCRIPTION:
{job_description}

Analyze it thoroughly and extract:

1. must_have_requirements     → non-negotiable musts (education, years exp, certs, skills)
2. preferred_skills           → nice-to-have / desired
3. key_responsibilities       → main duties (bullet list)
4. company_culture_indicators → inferred values, environment, work style
5. keywords_for_ats           → important phrases/words for ATS
6. red_flags                  → anything unusual, concerning or high-risk
7. positioning_strategy       → 2–4 sentences: how applicant should frame experience

CRITICAL RULES — FOLLOW EXACTLY:
- Output **ONLY** valid JSON — nothing else
- NO explanations, NO introductions, NO "Here is...", NO markdown, NO ```json fences
- Start directly with {{ and end with }}
- Use the exact keys shown below (no extra/missing keys)
- Lists must be arrays of strings
- Return clean, minimal JSON

Expected output format (copy this structure exactly):
{{
  "job_title": "{job_title}",
  "agency": "{agency}",
  "must_have_requirements": [],
  "preferred_skills": [],
  "key_responsibilities": [],
  "company_culture_indicators": [],
  "keywords_for_ats": [],
  "red_flags": [],
  "positioning_strategy": ""
}}
"""

        # Pass prompt as positional argument (no 'inputs=')
        raw_result = self.agent.kickoff(prompt)

        print(f"[ANALYZER] Raw result length: {len(str(raw_result))}")

        parsed = self._extract_json(str(raw_result))

        if "error" in parsed:
            print(f"[ANALYZER] Parsing failed → {parsed['error']}")
        else:
            print("[ANALYZER] Successfully parsed JSON")

        return parsed

     except Exception as e:
        print(f"[ANALYZER] Exception: {str(e)}")
        return {"critical_error": str(e), "raw_error_type": type(e).__name__}

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Improved robust JSON extraction"""
        if not text:
            return {"error": "Empty response from LLM"}

        # Strip common wrappers
        text = re.sub(r'```(?:json)?\s*|\s*```', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = text.strip()

        # Find outermost JSON
        match = re.search(r'\{[\s\S]*\}', text, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                parsed = json.loads(json_str)
                parsed.setdefault('raw_response', text)  # optional for debugging
                return parsed
            except json.JSONDecodeError as e:
                return {
                    "error": f"JSON decode failed: {str(e)}",
                    "raw_snippet": json_str[:400] + "..." if len(json_str) > 400 else json_str,
                    "raw_full": text[:1200]
                }

        return {
            "error": "No JSON object found in response",
            "raw_response": text[:1500]
        }