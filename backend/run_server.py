import sys
import os

# Add the current directory to sys.path to allow absolute imports of submodules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime

from fastapi import UploadFile, File, BackgroundTasks, Request
from apscheduler.schedulers.background import BackgroundScheduler
from notifier import Notifier
from internship import Internship, InternshipReport
from searcher import Searcher
from processor import Processor
from profile_manager import ProfileManager
from email_listener import EmailListener
from telegram_listener import TelegramListener
from whatsapp_listener import create_whatsapp_handler
from contextlib import asynccontextmanager
import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler
    if not scheduler.running:
        scheduler.start()
        # Daily scan by default
        if not scheduler.get_job('discovery_scan'):
            scheduler.add_job(perform_scheduled_scan, 'interval', hours=24, id='discovery_scan')
        print("Background scheduler started (Daily scans).")
    
    # Start Email Listener
    def email_callback(query: str):
        print(f"Email Callback Triggered for query: {query}")
        handle_message_trigger(query, source="Email")

    email_listener = EmailListener(email_callback)
    email_thread = threading.Thread(target=email_listener.start_polling, kwargs={'interval': 30}, daemon=True)
    email_thread.start()

    # Start Telegram Listener
    profile = profile_manager.profile
    tg_token = profile.get("telegram_token")
    tg_chat_id = profile.get("telegram_chat_id")
    
    if tg_token and tg_chat_id:
        def telegram_callback(query: str):
            print(f"Telegram Callback Triggered for query: {query}")
            handle_message_trigger(query, source="Telegram")
            
        tg_listener = TelegramListener(telegram_callback, tg_token, tg_chat_id)
        tg_thread = threading.Thread(target=tg_listener.start_polling, kwargs={'interval': 5}, daemon=True)
        tg_thread.start()
    else:
        print("Telegram Listener: Credentials missing in profile. Skipping.")
    
    yield
    # Shutdown scheduler
    if scheduler.running:
        scheduler.shutdown()
        print("Background scheduler shut down.")

app = FastAPI(title="Internship Discovery Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

profile_manager = ProfileManager()
searcher = Searcher()
scheduler = BackgroundScheduler()

def handle_message_trigger(query: str, source: str = "Trigger"):
    """
    Unified handler for scans initiated by Email, Telegram, or WhatsApp.
    """
    try:
        log_msg = f"[{datetime.now()}] Processing {source} trigger for: {query}"
        print(log_msg)
        with open("discovery_debug.log", "a") as f:
            f.write(f"{log_msg}\n")
            
        profile = profile_manager.profile
        
        # 1. Search
        print(f"[{datetime.now()}] Starting search for: {query}")
        search_results = searcher.automated_search(query)
        print(f"[{datetime.now()}] Search completed. Found {len(search_results)} results.")
        
        # 2. Process and Filter
        processor = Processor(profile)
        ranked = processor.filter_and_rank(search_results)
        print(f"[{datetime.now()}] Ranking completed. {len(ranked)} jobs ranked.")
        
        # 3. Notify
        high_matches = ranked[:5] 
        if high_matches:
            print(f"[{datetime.now()}] Preparing notification for top {len(high_matches)} matches.")
            notifier = Notifier(
                profile.get("email", "user@example.com"),
                telegram_token=profile.get("telegram_token"),
                telegram_chat_id=profile.get("telegram_chat_id")
            )
            msg_file = notifier.draft_internship_summary(high_matches)
            
            success_msg = f"[{datetime.now()}] {source} trigger processed. Results drafted to {msg_file}"
            print(success_msg)
            with open("discovery_debug.log", "a") as f:
                f.write(f"{success_msg}\n")
        else:
            print(f"[{datetime.now()}] No high-match results for {source} trigger.")
            
    except Exception as e:
        error_msg = f"[{datetime.now()}] Error handling {source} trigger: {str(e)}"
        print(error_msg)
        with open("backend_errors.log", "a") as f:
            f.write(f"{error_msg}\n")

def perform_scheduled_scan():
    """
    Background job to scan for new internships based on profile keywords.
    """
    try:
        print(f"[{datetime.now()}] Performing scheduled scan...")
        profile = profile_manager.profile
        # 1. Get jobs (Live & Local)
        target_roles = profile.get("target_roles", ["internship"])
        raw_results = []
        for role in target_roles:
            raw_results.extend(searcher.automated_search(role))
        
        # deduplication handled by searcher.save_discovered_jobs
        print(f"Loaded {len(raw_results)} jobs for scan.")
        
        # 2. Process and Filter
        processor = Processor(profile)
        ranked = processor.filter_and_rank(raw_results)
        print(f"Ranked {len(ranked)} jobs.")
        
        # 3. Notify if high matches found
        high_matches = [j for j in ranked if j.match_score >= 70]
        debug_msg = f"Scan Result: Total={len(ranked)}, HighMatches={len(high_matches)}\n"
        for j in ranked[:5]: # Log top 5
            debug_msg += f" - {j.company_name} | {j.role_title}: Score {j.match_score}\n"
        
        with open("discovery_debug.log", "a") as f:
             f.write(f"[{datetime.now()}] {debug_msg}\n")
             
        if high_matches:
            notifier = Notifier(
                profile.get("email", "user@example.com"),
                telegram_token=profile.get("telegram_token"),
                telegram_chat_id=profile.get("telegram_chat_id")
            )
            notifier.draft_internship_summary(high_matches)
        
        # Update last scan time
        profile_manager.profile["last_scan"] = datetime.now().isoformat()
        profile_manager.save_profile(profile_manager.profile)
    except Exception as e:
        error_msg = f"ERROR in background scan: {str(e)}"
        print(error_msg)
        with open("backend_errors.log", "a") as f:
            f.write(f"[{datetime.now()}] {error_msg}\n")


@app.post("/scan/now")
async def trigger_scan_now(background_tasks: BackgroundTasks):
    background_tasks.add_task(perform_scheduled_scan)
    return {"message": "Scan triggered in background"}

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    WhatsApp webhook to handle incoming messages.
    """
    def whatsapp_callback(query: str):
        print(f"WhatsApp Callback Triggered for query: {query}")
        handle_message_trigger(query, source="WhatsApp")
        
    handler = create_whatsapp_handler(whatsapp_callback)
    return await handler(request)

@app.get("/")
def read_root():
    return {"status": "Internship Discovery Agent is running"}

@app.get("/profile")
def get_profile():
    return profile_manager.profile

@app.post("/profile/update")
def update_profile(profile_data: dict):
    updated = profile_manager.save_profile(profile_data)
    return {"message": "Profile updated successfully", "profile": updated}

@app.post("/profile/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    print(f"Received resume upload request: {file.filename}")
    if not file.filename.endswith(".pdf"):
        print(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently.")
    
    try:
        content = await file.read()
        print(f"File read successful, size: {len(content)} bytes")
        
        text = profile_manager.extract_text_from_pdf(content)
        if not text:
            print("Failed to extract text from PDF")
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF.")
        
        print(f"Text extracted successfully, length: {len(text)} characters")
        
        # Simple extraction logic
        extracted_details = profile_manager.parse_resume_to_profile(text)
        print(f"Extracted details: {extracted_details}")
        
        profile_manager.save_profile(extracted_details)
        print("Profile updated successfully with resume details")
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "extracted_skills": extracted_details.get("skills", []),
            "profile": profile_manager.profile
        }
    except Exception as e:
        print(f"Error during resume processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/discover", response_model=InternshipReport)
def discover_internships(keywords: Optional[str] = None):
    try:
        current_profile = profile_manager.profile
        
        # If no keywords provided, use target roles from profile
        if not keywords:
            roles = current_profile.get("target_roles", [])
            if roles:
                keywords = ", ".join(roles)
            else:
                keywords = "internship" # Broad fallback
            
        print(f"Beginning discovery for keywords: {keywords}")
        
        processor = Processor(current_profile)
        
        # 1. Search (reading real data populated by the agent)
        raw_results = searcher.get_discovered_jobs()
        print(f"Total raw jobs loaded: {len(raw_results)}")
        
        # Filter raw results by keywords if they exist (lenient word-based matching)
        if keywords:
            search_terms = []
            # Split keywords by commas and then by spaces for individual words
            for k in keywords.split(','):
                search_terms.extend([word.strip().lower() for word in k.split() if len(word.strip()) > 2])
            
            # De-duplicate words
            search_terms = list(set(search_terms))
            print(f"Refined search words: {search_terms}")
            
            filtered_results = []
            for job in raw_results:
                job_text = f"{job.role_title} {job.company_name} {' '.join(job.required_skills)}".lower()
                # Check if ANY of our key words are present in the job text
                if any(term in job_text for term in search_terms):
                    filtered_results.append(job)
            
            print(f"Jobs matching keywords: {len(filtered_results)}")
            raw_results = filtered_results

        ranked_results = processor.filter_and_rank(raw_results)
        top_3 = ranked_results[:3]
        urgent = [i for i in ranked_results if i.is_high_priority]
        
        report = InternshipReport(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_found=len(ranked_results),
            internships=ranked_results,
            top_recommendations=top_3,
            urgent_deadlines=urgent
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting Internship Discovery Agent API on http://0.0.0.0:8011")
    uvicorn.run("run_server:app", host="0.0.0.0", port=8011, reload=False)
