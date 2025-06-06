from scrape_search_results import run_search_scraper
from scrape_job_details import scrape_job_details
from process_new_jobs import process_new_jobs
from send_applications import send_applications

def main():
    print("🔍 Step 1: Scraping job search results...")
    run_search_scraper()
    
    print("📄 Step 2: Scraping individual job pages...")
    scrape_job_details()

    print("🤖 Step 3: Generating outreach applications via AI...")
    process_new_jobs()

    print("✉️ Step 4: Sending applications...")
    send_applications()

    print("✅ All steps complete!")

if __name__ == "__main__":
    main()
