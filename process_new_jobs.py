import sqlite3
from ai.outreach_agent import generate_outreach
import time

DB_PATH = "jobs.db"  # adjust if your DB is elsewhere

def process_new_jobs():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # 1. Fetch jobs that don't have an application linked
    cur.execute("""
        SELECT *
        FROM jobs
        WHERE application_id IS NULL
        ORDER BY date_added ASC
        LIMIT 20
    """)
    jobs = cur.fetchall()

    print(f"🔎 Found {len(jobs)} job(s) needing applications.\n")

    for job in jobs:
        job_id = job["job_id"]
        print(f"📝 Processing job_id={job_id} | {job['title']}")

        # Defensive check: skip if job description is empty
        if not job["job_description"]:
            print(f"  ⚠️  Skipping (empty job_description)")
            continue

        # 2. Generate application via AI
        try:
            result = generate_outreach(
                job_title=job["title"],
                company=job["company"],
                job_description=job["job_description"],
                instructions=job["instructions"] or "",
            )
        except Exception as e:
            print(f"  ❌ Error generating application: {e}")
            continue

        # 3. Insert new row into applications
        cur.execute("""
            INSERT INTO applications
                (job_id, ai_category, resume_used, email_subject, email_body, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            result.category,
            result.resume_file,
            result.email_subject,
            result.email_body,
            result.notes
        ))
        application_id = cur.lastrowid

        # 4. Update jobs.application_id with the new application’s id
        cur.execute("""
            UPDATE jobs
            SET application_id = ?
            WHERE job_id = ?
        """, (application_id, job_id))

        con.commit()
        print(f"  ✅ Application generated and linked. application_id={application_id}")
        time.sleep(1.5)  # optional: pause to avoid API rate limits

    con.close()
    print("\n🎉 Done processing new jobs.")

if __name__ == "__main__":
    process_new_jobs()
