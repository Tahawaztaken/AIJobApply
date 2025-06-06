import sqlite3

DB_PATH = "jobs.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect_db() as conn:
        cursor = conn.cursor()

        # Create jobs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            salary_min REAL,
            salary_max REAL,
            salary_type TEXT,
            posted_date TEXT,
            job_url TEXT,
            job_description TEXT, 
            email TEXT,           
            instructions TEXT,    
            application_id INTEGER, 
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id)
        )
        """)

        # Create applications table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            ai_category TEXT,
            resume_used TEXT,
            email_body TEXT,
            notes TEXT,
            date_applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        )
        """)

        conn.commit()

def insert_job(job):
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO jobs 
                (job_id, title, company, location, salary_min, salary_max, salary_type, posted_date, job_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job['job_number'] or job['link'],  
                job['title'],
                job['company'],
                job['location'],
                job['salary_min'],
                job['salary_max'],
                job['salary_type'],
                job['posted_date'],
                job['link']
            ))
            conn.commit()
        except sqlite3.Error as e:
            print("❌ Error inserting job:", e)

def get_unapplied_jobs():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE applied = 0")
        return cursor.fetchall()
