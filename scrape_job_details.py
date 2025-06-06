from playwright.sync_api import sync_playwright, TimeoutError
import sqlite3
from db.db import connect_db 

def get_pending_jobs():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT job_id, job_url FROM jobs WHERE email IS NULL")
        return cursor.fetchall()

def update_job_details(job_id, description, email, instructions):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE jobs 
            SET job_description = ?, email = ?, instructions = ?
            WHERE job_id = ?
        """, (description, email, instructions, job_id))
        conn.commit()

def extract_job_info(page):
    try:
        # Click "Show how to apply" if present
        if page.locator("#applynowbutton").is_visible():
            page.click("#applynowbutton")
            page.wait_for_timeout(1500)
    except:
        pass  # Button not present or already expanded

    # ✏️ Extract description from #comparisonchart
    try:
        chart = page.locator("#comparisonchart")
        sections = chart.locator("h4, h3, li, p")

        description_parts = []
        for i in range(sections.count()):
            el = sections.nth(i)
            tag = el.evaluate("el => el.tagName.toLowerCase()")
            text = el.inner_text().strip()

            if tag in ["h3", "h4"]:
                description_parts.append(f"\n\n{text.upper()}")
            elif tag == "li":
                description_parts.append(f"- {text}")
            elif tag == "p":
                if text:  # avoid empty <p>
                    description_parts.append(f"{text}")

        description = "\n".join(description_parts).strip()
    except Exception as e:
        print(f"⚠️ Failed to parse description: {e}")
        description = "N/A"

    # 📬 Extract email
    try:
        email_elem = page.locator("#howtoapply a[href^='mailto:']")
        email = email_elem.inner_text().strip() if email_elem else "N/A"
    except:
        email = "N/A"

    # 📄 Extract instructions
    try:
        instructions_elem = page.locator("#howtoapply").inner_text().strip()
        instructions = instructions_elem if instructions_elem else "N/A"
    except:
        instructions = "N/A"

    return description, email, instructions


def scrape_job_details():
    jobs = get_pending_jobs()
    print(f"🔎 Found {len(jobs)} new jobs to process.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=80)
        page = browser.new_page()

        for job_id, url in jobs:
            try:
                print(f"🌐 Visiting {url}")
                page.goto(url, timeout=10000)
                page.wait_for_selector("#applynow", timeout=5000)

                description, email, instructions = extract_job_info(page)
                update_job_details(job_id, description, email, instructions)
                print(f"✅ Updated job {job_id}")

            except TimeoutError:
                print(f"❌ Timeout on job {job_id}")
            except Exception as e:
                print(f"❌ Error on job {job_id}: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_job_details()
