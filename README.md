# AIJobApply

This project automates scraping job postings, generating outreach emails using OpenAI and sending them via Gmail.

## Setup

1. Create a `.env` file in the project root with the following variables:

```bash
OPENAI_API_KEY=your_openai_key
SENDER_EMAIL=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
```

2. Place your resume PDFs inside the `resumes/` folder. These will be attached to outgoing applications and used for AI matching.

3. Run the pipeline:

```bash
python run_pipeline.py
```

## Testing the outreach agent

You can try the AI generation step on its own with:

```bash
python tests/test_outreach.py
```

The script lets you select a job from the database or paste a description and prints both the prompt and the JSON returned by OpenAI.
