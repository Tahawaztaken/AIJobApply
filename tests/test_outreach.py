"""Manual tester for the outreach agent.

Run without arguments to pick a recent job from the database.
Use --job JOB_ID to test a specific job.
Use --paste to enter a description manually.
"""
import argparse
import sqlite3
from dotenv import load_dotenv
from ai.outreach_agent import generate_outreach

DB_PATH = "jobs.db"


def fetch_job(job_id: str):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT job_id, title, company, job_description, instructions FROM jobs WHERE job_id = ?",
        (job_id,),
    ).fetchone()
    con.close()
    return row


def pick_job_interactively():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT job_id, title FROM jobs ORDER BY date_added DESC LIMIT 25"
    ).fetchall()
    con.close()

    print("\nRecent jobs in DB:")
    for idx, r in enumerate(rows, 1):
        print(f"{idx:2d}. {r['job_id']} | {r['title'][:60]}")

    choice = int(input("\nSelect a row number → "))
    return fetch_job(rows[choice - 1]["job_id"])


def main():
    load_dotenv()

    ap = argparse.ArgumentParser(
        description="Quickly test the outreach agent with real jobs or pasted text."
    )
    ap.add_argument("--job", help="job_id to test from DB")
    ap.add_argument("--paste", action="store_true", help="manually paste description/title")
    args = ap.parse_args()

    if args.paste:
        title = input("Enter job title: ").strip()
        company = input("Enter company: ").strip()
        print("\nPaste the full job description. End with an empty line:")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        description = "\n".join(lines)
        instructions = input("\nPaste any application instructions (or leave blank): ").strip()
    else:
        row = fetch_job(args.job) if args.job else pick_job_interactively()
        if not row:
            print("❌ job_id not found.")
            return
        title = row["title"]
        company = row["company"]
        description = row["job_description"]
        instructions = row["instructions"] or ""

    print("\n⏳ Calling OpenAI…")
    prompt, result = generate_outreach(
        job_title=title,
        company=company,
        job_description=description,
        instructions=instructions,
        return_prompt=True,
    )

    print("\n📤 Prompt sent to AI:")
    print("=" * 80)
    print(prompt)

    print("\n✅ Response:")
    print("=" * 80)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
