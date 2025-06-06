from playwright.sync_api import sync_playwright
import json
import re

BASE_URL = "https://www.jobbank.gc.ca"

def parse_salary(salary_text: str):
    # Remove leading "Salary:" and extra whitespace
    salary_text = salary_text.replace("Salary:", "").strip()

    # Find all numeric values (handle both $1,000.00 and $30)
    matches = re.findall(r"\$?([\d,]+(?:\.\d{1,2})?)", salary_text)

    # Convert matches to float
    salary_numbers = [float(m.replace(",", "")) for m in matches]

    # Try to detect salary type (hourly, annually, etc.)
    salary_type_match = re.search(r"(hourly|annually|biweekly|monthly)", salary_text, re.IGNORECASE)
    salary_type = salary_type_match.group(1).lower() if salary_type_match else "unspecified"

    # Assign min/max or single value
    if len(salary_numbers) == 2:
        return salary_numbers[0], salary_numbers[1], salary_type
    elif len(salary_numbers) == 1:
        return salary_numbers[0], salary_numbers[0], salary_type
    else:
        return None, None, salary_type

def scrape_jobbank_search_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=80)
        page = browser.new_page()

        url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=30&fcid=296305&fcid=296420&fcid=296425&fn21=21223&term=data+analyst&page=1&sort=D&fsrc=16"
        page.goto(url)

        page.wait_for_selector("#ajaxupdateform\\:result_block article")
        MAX_LOAD_MORE = 3
        for i in range(MAX_LOAD_MORE):
            try:
                load_more_btn = page.query_selector("#moreresultbutton")
                if load_more_btn:
                    print(f"🔁 Clicking 'Show more results' button (round {i+1})...")
                    load_more_btn.click()
                    page.wait_for_timeout(2000)  # Wait for new results to load
                else:
                    print("✅ No more 'Show more' button found.")
                    break
            except Exception as e:
                print(f"⚠️ Error trying to click 'Show more' button: {e}")
                break
        articles = page.query_selector_all("#ajaxupdateform\\:result_block article")

        jobs = []
        for article in articles:
            try:
                anchor = article.query_selector("a.resultJobItem")
                href = anchor.get_attribute("href")
                link = BASE_URL + href

                title_el = anchor.query_selector("h3 span.noctitle")
                title = title_el.inner_text().strip() if title_el else "N/A"

                company_el = anchor.query_selector("ul li.business")
                company = company_el.inner_text().strip() if company_el else "N/A"

                location_el = anchor.query_selector("ul li.location")
                raw_location = location_el.inner_text().strip() if location_el else "N/A"
                location = raw_location.replace("Location", "").strip()

                salary_el = anchor.query_selector("ul li.salary")
                raw_salary = salary_el.inner_text().strip() if salary_el else "N/A"
                salary_min, salary_max, salary_type = parse_salary(raw_salary)

                date_el = anchor.query_selector("ul li.date")
                posted_date = date_el.inner_text().strip() if date_el else "N/A"

                job_id_el = anchor.query_selector("ul li.source")
                job_number = "N/A"
                if job_id_el:
                    full_text = job_id_el.inner_text().strip()
                    lines = full_text.split("\n")
                    for line in lines:
                        if line.strip().isdigit():
                            job_number = line.strip()
                            break

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_type": salary_type,
                    "posted_date": posted_date,
                    "job_number": job_number,
                    "link": link
                })

            except Exception as e:
                print(f"⚠️ Error processing job: {e}")

        # Save output
        with open("jobbank_search_results.json", "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)

        print(f"✅ Extracted {len(jobs)} job postings.")
        browser.close()

if __name__ == "__main__":
    scrape_jobbank_search_page()
