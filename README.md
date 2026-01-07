# CourseScoutAgent(Project In Progress)

CourseScoutAgent is an automated background agent that discovers time-sensitive free courses, verifies that links and vouchers are still valid, filters for high-value software engineering topics, and sends Telegram / Email alerts so students don’t miss real opportunities.

---

## Motivation

Free course vouchers are often shared on LinkedIn and Reddit, but many expire quickly or lead to invalid links by the time users see them.

CourseScoutAgent solves this by:

- Monitoring multiple sources continuously  
- Validating links immediately  
- Filtering out low-value or irrelevant content  
- Notifying users only when a course is actually usable  

---

## Key Features

### Multi-source discovery (MVP)
- Reddit: r/udemyfreebies, r/FreeUdemyCoupons  
- LinkedIn (planned – Phase 2)

### Deterministic voucher & link validation
- Detects expired coupons, invalid redirects, or closed enrollments  
- Marks results as **VALID / INVALID / UNKNOWN**

### AI-assisted quality filtering
Scores usefulness for software engineering career growth and classifies topics such as:
- Programming Languages  
- DevOps / Cloud  
- Industry Certifications (AWS, Microsoft, etc.)  
- Data Structures & Algorithms  
- AI / ML / AI Agents  
- LeetCode / Interview Preparation  

### Notifications
- Telegram alerts (MVP)  
- Email notifications (optional / Phase 2)

### User-controlled enrollment
- No automatic registration by default  
- Enrollment automation is optional and depends on platform support and explicit user consent  

---

## System Overview

The agent is implemented as a pipeline:

1. **Collector**  
   Fetches posts from supported sources and extracts text and links.

2. **Validator (non-AI)**  
   Checks whether a course link or voucher is valid at the time of detection.

3. **Scorer (AI layer)**  
   Evaluates relevance and usefulness for software engineering students and job seekers.

4. **Notifier**  
   Sends alerts only for validated and high-quality opportunities.

5. **Storage**  
   Persists posts, validation results, deduplication keys, and notification state.

---

## MVP vs Future Roadmap

### MVP
- Reddit collector  
- SQLite storage  
- Udemy-focused validator  
- AI topic classification & usefulness scoring  
- Telegram notifications  
- Deduplication (no repeated alerts)

### Future Enhancements
- LinkedIn collector (Playwright)  
- Additional course platforms  
- Personalization (user preferences & goals)  
- Web dashboard (optional)  
- Feedback loop 
- Queue-based processing (Celery / Redis)  
- PostgreSQL for scale  

---

## Tech Stack

- **Language:** Python  
- **Collectors:** Reddit API (MVP), Playwright (Phase 2)  
- **Validation:** httpx / requests + rule-based detectors  
- **AI:** LLM for extraction, classification, and scoring  
- **Storage:** SQLite (MVP) → PostgreSQL (later)  
- **Notifications:** Telegram Bot API, Email provider  
- **Scheduling:** cron / APScheduler  
- **Deployment:** Docker, GitHub Actions  

---

## Project Structure (Planned)

```
CourseScoutAgent/
  src/
    collectors/
    extractors/
    validators/
    scoring/
    notifiers/
    storage/
    config/
    main.py
  tests/
  README.md
  requirements.txt
  .env.example
```

---

## Running the Project (MVP)

1. Clone the repository  
2. Create `.env` from `.env.example`  
3. Install dependencies  
4. Run locally:

```bash
python -m src.main --once
```

5. Schedule periodic execution using cron or APScheduler

---

## Notes on Compliance

- Reddit is used as the initial data source due to API accessibility  
- LinkedIn automation is planned carefully and added only after MVP stability  
- The project avoids storing sensitive personal data  

---

## License

MIT
