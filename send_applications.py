import sqlite3
import yagmail
import time
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "jobs.db")
RESUME_DIR = os.getenv("RESUME_DIR", "resumes")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def send_applications():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Fetch all jobs/applications ready to send
    cur.execute("""
        SELECT j.job_id, j.email AS recipient, j.title, j.company, a.id AS app_id,
               a.email_subject, a.email_body, a.resume_used
        FROM jobs j
        JOIN applications a ON j.application_id = a.id
        WHERE a.date_applied IS NULL AND j.email IS NOT NULL AND j.email != ''
        LIMIT 30
    """)
    to_send = cur.fetchall()

    if not to_send:
        print("No pending applications to send.")
        return

    yag = yagmail.SMTP(SENDER_EMAIL, GMAIL_APP_PASSWORD)

    for row in to_send:
        recipient = row["recipient"]
        
        # recipient = "syedtahafaisal123@gmail.com"
        subject = row["email_subject"]
        body = row["email_body"]
        company = row["company"] or ""
        resume_filename = row["resume_used"]
        resume_path = os.path.join(RESUME_DIR, resume_filename) if resume_filename else None

        print(f"\n➡️  Sending application to {recipient} for '{row['title']}'...")

        try:
            if not os.path.isfile(resume_path):
                print(f"  ⚠️  Resume file not found: {resume_path}. Skipping.")
                continue
            # ---- GREETING (always on top, with double <br> after)
            greeting = f"Hi {company.strip()} Team,<br>" if company.strip() else "Hello,<br>"

            # ---- FOOTER (compact, HTML)
            footer_html = (
                "Best regards,<br>"
                "Taha Faisal<br>"
                "📧 <a href=\"mailto:tahafaisalapps@gmail.com\">tahafaisalapps@gmail.com</a><br>"
                "🔗 <a href=\"https://tahawaztaken.github.io/Portfolio2/\" target=\"_blank\">Portfolio</a> | "
                "<a href=\"https://www.linkedin.com/in/taha-faisal\" target=\"_blank\">LinkedIn</a>"
            )

            # footer_html = """
            # Best regards,
            # Taha Faisal
            # 📧 <a href="mailto:tahafaisalapps@gmail.com">tahafaisalapps@gmail.com</a>
            # 🔗 <a href="https://tahawaztaken.github.io/Portfolio2/" target="_blank">Portfolio</a> | <a href="https://www.linkedin.com/in/taha-faisal" target="_blank">LinkedIn</a>
            # """

            email_body = f"{greeting}{body}{footer_html}"

            yag.send(
                to=recipient,
                subject=subject,
                contents=[email_body],
                attachments=[resume_path]
            )

            # Update date_applied
            cur.execute("UPDATE applications SET date_applied = CURRENT_TIMESTAMP WHERE id = ?", (row["app_id"],))
            conn.commit()
            print("  ✅ Email sent and application marked as applied.")
            time.sleep(120) 

        except Exception as e:
            print(f"  ❌ Failed to send email: {e}")

    conn.close()

if __name__ == "__main__":
    send_applications()
