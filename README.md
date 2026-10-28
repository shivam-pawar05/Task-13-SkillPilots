# MySQL Checksum Verification

Python project to calculate SHA-256 checksums for MySQL tables, compare them with trusted reference checksums, log results, and email alerts for mismatches.

## Setup (Windows)
1. Run `sql/setup.sql` in MySQL Workbench.
2. Copy `.env.example` to `.env` and update database/SMTP settings.
3. Run `python -m venv .venv`
4. Run `.venv\Scripts\activate`
5. Run `pip install -r requirements.txt`
6. Create the trusted baseline: `python main.py --initialize-baseline`
7. Verify: `python main.py`

## Nightly scheduling
Use Windows Task Scheduler with the full path to `.venv\Scripts\python.exe`, argument `main.py`, and the project directory as “Start in”. Ensure the task account can access `.env`.

## Notes
Tables need primary keys. The initial baseline must be created from trusted data. Legitimate changes produce mismatches until reviewed. For actively changing tables, use suitable snapshot/transaction controls. Never commit `.env` or credentials.
