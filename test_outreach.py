"""
Manual test runner for the outreach agent.

Usage
-----
python test_outreach.py                # interactively choose a DB row
python test_outreach.py --job JOB_ID   # test a specific job_id from DB
python test_outreach.py --paste        # paste a raw description in terminal
"""

import argparse
import sqlite3
from ai.outreach_agent import generate_outreach

DB_PATH = "jobs.db"  # ← change if your DB lives elsewhere


def fetch_job(job_id: str):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT job_id, title, company, job_description, instructions "
        "FROM jobs WHERE job_id = ?",
        (job_id,)
    ).fetchone()
    con.close()
    return row


def pick_job_interactively():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT job_id, title, company FROM jobs ORDER BY date_added DESC LIMIT 25"
    ).fetchall()
    con.close()

    print("\nRecent jobs in DB:")
    for idx, r in enumerate(rows, 1):
        print(f"{idx:2d}. {r['job_id']}  |  {r['title'][:60]}")

    choice = int(input("\nSelect a row number → "))
    row = rows[choice - 1]
    return fetch_job(row["job_id"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", help="job_id to test from DB")
    ap.add_argument("--paste", action="store_true",
                    help="manually paste description/title")
    args = ap.parse_args()

    if args.paste:
        title = input("Enter job title: ").strip()
        company = input("Enter company: ").strip()
        print("\nPaste full job description. End with an empty line:")
        lines, line = [], None
        while line != "":
            line = input()
            lines.append(line)
        description = "\n".join(lines)
        instructions = input("\nPaste any application instructions (or leave blank): ").strip()
    else:
        if not args.job:
            row = pick_job_interactively()
        else:
            row = fetch_job(args.job)

        if not row:
            print("❌ job_id not found.")
            return

        title        = row["title"]
        company      = row["company"]
        description  = row["job_description"]
        instructions = row["instructions"] or ""

    print("\n⏳ Calling AI …")
    user_prompt, result = generate_outreach(
        job_title=title,
        company=company,
        job_description=description,
        instructions=instructions,
        return_prompt=True
    )

    print("\n📤 Prompt sent to AI:")
    print("=" * 80)
    print(user_prompt)

    print("\n✅ Response:")
    print("=" * 80)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
