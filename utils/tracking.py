import os
import csv
from datetime import datetime
from utils.config import COVER_LETTERS_DIR,APPLICATIONS_LOG_PATH

def save_cover_letter_file(cover_letter_text:str,job_title:str,agency:str)->str:
    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_job_title="".join(c for c in job_title if c.isalnum() or c in (' ','-','_')).rstrip()
    safe_job_title=safe_job_title.replace(' ','_')[:50]
    filename=f"cover_letter_{safe_job_title}_{timestamp}.txt"
    filepath=os.path.join(COVER_LETTERS_DIR,filename)
    with open(filepath,'w',encoding='utf-8') as f:
        f.write(f"Cover letter for {job_title}\n")
        f.write(f"Agency:{agency}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n" + "="*50 + "\n\n")
        f.write(cover_letter_text)
    print(f"Cover letter saved to :{filepath}")
    return filepath
def log_application(job_id:str,job_title:str,agency:str,resume_summary:str,cover_letter_path:str,status:str="applied")->None:
     """
    Log application details to the applications log CSV file
    
    Args:
        job_id: The USAJobs job ID
        job_title: The job title
        agency: The agency/company name
        resume_summary: Brief summary of resume customization
        cover_letter_path: Path to the saved cover letter
        status: Application status (default: "applied")
    """
     file_exists=os.path.isfile(APPLICATIONS_LOG_PATH)
     with open(APPLICATIONS_LOG_PATH,'a',newline='',encoding='utf-8') as f:
         writer=csv.writer(f)
         if not file_exists:
              writer.writerow([
                'timestamp', 'job_id', 'job_title', 'agency', 
                'resume_summary', 'cover_letter_path', 'status'
            ])
         writer.writerow([
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             job_id,
             job_title,
             agency,
             resume_summary[:200],
             cover_letter_path,
             status
         ])
     print(f"Application logged for {job_title}")
     
         
    
        