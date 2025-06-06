from playwright.sync_api import sync_playwright
import json
import re
from db.db import init_db, insert_job

BASE_URL = "https://www.jobbank.gc.ca"

def parse_salary(salary_text: str):
    salary_text = salary_text.replace("Salary:", "").strip()
    matches = re.findall(r"\$?([\d,]+(?:\.\d{1,2})?)", salary_text)
    salary_numbers = [float(m.replace(",", "")) for m in matches]
    salary_type_match = re.search(r"(hourly|annually|biweekly|monthly)", salary_text, re.IGNORECASE)
    salary_type = salary_type_match.group(1).lower() if salary_type_match else "unspecified"
    if len(salary_numbers) == 2:
        return salary_numbers[0], salary_numbers[1], salary_type
    elif len(salary_numbers) == 1:
        return salary_numbers[0], salary_numbers[0], salary_type
    else:
        return None, None, salary_type
def run_search_scraper():
    init_db()
    # search_urls = [
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&fcid=3763&fcid=3770&fcid=3776&fcid=3949&fcid=3950&fcid=297234&fn21=20012&fn21=21231&fn21=21232&fn21=21234&term=developer%2C+web+developer&term=software&page=1&sort=D&fprov=ON&fsrc=16",
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&fn21=21232&sort=D&fprov=ON&fsrc=16",
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&fcid=3001&fcid=3019&fcid=3739&fcid=5395&fcid=15885&fcid=22534&fcid=22887&fcid=25803&fcid=296425&fcid=296531&fcid=297197&fcid=297520&fn21=12010&fn21=20012&fn21=21211&fn21=21223&term=data&page=1&sort=D&fprov=ON&fsrc=16",
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&fcid=5741&fcid=5753&fcid=12348&fcid=12351&fcid=20945&fcid=24755&fcid=296544&fcid=296623&fn21=21233&fn21=21234&fn21=22220&term=web&sort=D&fsrc=16",
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&fcid=5248&fn21=21223&term=database&sort=D&fsrc=16",
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&empl=office&sort=D&fprov=ON&fsrc=16",
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&fcid=3763&fcid=3770&fcid=3776&fcid=3949&fcid=3950&fcid=297234&fn21=20012&fn21=21231&fn21=21232&term=software&sort=D&fprov=ON&fsrc=16",
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&fn21=13110&fn21=13112&sort=D&fprov=ON&fsrc=16",
    #     "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=2&fcid=15940&fcid=17873&fcid=22507&fcid=27177&fcid=295849&fcid=295918&fcid=296085&fcid=296811&fcid=296823&fcid=296881&fn21=20012&fn21=21220&fn21=22221&term=information+technology&sort=D&fprov=ON&fsrc=16"
    # ]

    search_urls = [
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=21230&sort=M&fprov=ON", #Computer systems developers and programmers 
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=21211&sort=M&fprov=ON&fsrc=16", #Data scientists
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=21223&sort=M&fprov=ON&fsrc=16", #Database analysts and data administrators
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=21222&sort=M&fprov=ON&fsrc=16", #Information systems specialists
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=21232&sort=M&fprov=ON&fsrc=16", #Software developers and programmers
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=21231&sort=M&fprov=ON&fsrc=16", #Software engineers and designers
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=21233&sort=M&fprov=ON&fsrc=16", #Web designers
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=21234&sort=M&fprov=ON&fsrc=16", #Web developers and programmers
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=22222&sort=M&fprov=ON&fsrc=16", #Information systems testing technicians
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=22221&sort=M&fprov=ON&fsrc=16", #User support technicians
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=20012&sort=M&fprov=ON&fsrc=16", #Computer and information systems managers
        "https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=12&fn21=41402&sort=M&fprov=ON&fsrc=16", #Business development officers and market researchers and analysts
    ]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=80)
        page = browser.new_page()

        all_jobs = []

        for url in search_urls:
            print(f"🌐 Scraping URL: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
            except Exception as e:
                print(f"❌ Failed to load {url}: {e}")
                continue

            try:
                page.wait_for_selector("#ajaxupdateform\\:result_block article", timeout=5000)
            except:
                print(f"⚠️ No job results found for: {url}")
                continue


            MAX_LOAD_MORE = 3
            for i in range(MAX_LOAD_MORE):
                try:
                    load_more_btn = page.query_selector("#moreresultbutton")
                    if load_more_btn:
                        print(f"🔁 Clicking 'Show more results' (round {i+1})...")
                        load_more_btn.click()
                        page.wait_for_timeout(2000)
                    else:
                        break
                except Exception as e:
                    print(f"⚠️ Load more error: {e}")
                    break

            articles = page.query_selector_all("#ajaxupdateform\\:result_block article")

            for article in articles:
                try:
                    anchor = article.query_selector("a.resultJobItem")
                    href = anchor.get_attribute("href")
                    link = BASE_URL + href

                    title = anchor.query_selector("h3 span.noctitle").inner_text().strip()
                    company = anchor.query_selector("ul li.business").inner_text().strip()
                    raw_location = anchor.query_selector("ul li.location").inner_text().strip()
                    location = raw_location.replace("Location", "").strip()

                    salary_el = anchor.query_selector("ul li.salary")
                    raw_salary = salary_el.inner_text().strip() if salary_el else "N/A"
                    salary_min, salary_max, salary_type = parse_salary(raw_salary)

                    posted_date = anchor.query_selector("ul li.date").inner_text().strip()

                    job_id_el = anchor.query_selector("ul li.source")
                    job_number = "N/A"
                    if job_id_el:
                        full_text = job_id_el.inner_text().strip()
                        for line in full_text.split("\n"):
                            if line.strip().isdigit():
                                job_number = line.strip()
                                break

                    job_data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary_min": salary_min,
                        "salary_max": salary_max,
                        "salary_type": salary_type,
                        "posted_date": posted_date,
                        "job_number": job_number,
                        "link": link
                    }

                    all_jobs.append(job_data)
                    insert_job(job_data)

                except Exception as e:
                    print(f"⚠️ Error processing job: {e}")

        with open("jobbank_search_results.json", "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)

        print(f"✅ Extracted {len(all_jobs)} jobs from {len(search_urls)} URLs.")
        browser.close()


if __name__ == "__main__":
    run_search_scraper()
