# GitHub Trending AI Daily (GTAD)

Automated daily reports of trending GitHub projects, analyzed by AI.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   Copy `.env.example` to `.env` and fill in your API keys.
   ```bash
   cp .env.example .env
   ```
   
   - **GITHUB_TOKEN**: Optional but recommended to avoid rate limits.
   - **GEMINI_API_KEY**: Required for AI analysis (Get it from Google AI Studio).
   - **SMTP_***: Your email provider details for sending the report.

3. **Run**
   ```bash
   python main.py
   ```

## Project Structure
- `src/`: Core logic (Scraper, LLM, Notifier).
- `templates/`: HTML email templates.
- `main.py`: Entry point.

## Automation
This script is designed to run via GitHub Actions or a Cron job.
