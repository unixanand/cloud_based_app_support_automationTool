# Production Support Automation Dashboard

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-brightgreen)](https://streamlit.io/) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) [![Supabase](https://img.shields.io/badge/Supabase-DB-orange)](https://supabase.com/)

A web-based dashboard built with **Streamlit** for monitoring and managing production environments. It integrates **system monitoring** (via `psutil`), **log analysis** (with Pandas), **service control** (via `systemctl` or Windows `sc`), and **batch job tracking** (via Supabase PostgreSQL). Alerts are sent via email for critical issues.

Key features include real-time health checks, log grepping, service management, and batch job oversight—ideal for DevOps/ProdOps teams automating support tasks.

## 🚀 Features

- **Health Monitor**: Track CPU, memory, disk, and network usage with visual metrics. Auto-alert via email if CPU > 80%.
- **Log Analyzer**: Upload CSV/TSV logs and grep for patterns (e.g., "ERROR|FAIL"). Visualize error trends with bar charts.
- **Service Manager**: List services (cgroups on Linux, query on Windows), check status, and start/stop/restart with sudo.
- **Batch Jobs**: View recent jobs from Supabase, retry failures, and display failures.
- **DB Alerts**: Scan for recent failures, compute failure rates, and email notifications for issues >20% or last 24h.
- **Batch Manager**: Placeholder console for manual batch operations (expandable).
- **Sidebar Navigation**: Easy module switching, refresh, and logout.
- **Cross-Platform**: Supports Linux (systemd) and Windows (sc query).
- **Secure Config**: Uses `.env` for Supabase and email credentials.

## 📋 Prerequisites

- Python 3.8+
- Git (for cloning)
- Supabase account (free tier works) with a `batch_jobs` table (see schema below).
- Gmail app password for email alerts (enable 2FA and generate one).

## 🛠️ Installation

1. **Clone the Repo**:
   ```
   git clone <your-repo-url>  # e.g., https://github.com/unixanand/cloud_based_app_support_automationTool
   cd cloud_based_app_support_automationTool
   ```

2. **Create Virtual Environment** (recommended):
   ```
   python -m venv venv
   # Activate: venv\Scripts\activate (Windows) or source venv/bin/activate (Linux/macOS)
   ```

3. **Install Dependencies**:
   ```
   pip install streamlit pandas psutil python-dotenv supabase python-dateutil
   ```
   - `smtplib` and `email` are built-in.
   - For Windows: Ensure `sc` (Service Control) is available (default on Win10+).

4. **Set Up Supabase**:
   - Create a project on [supabase.com](https://supabase.com).
   - Get your `SUPABASE_URL` and `SUPABASE_ANON_KEY` from Settings > API.
   - Create a `batch_jobs` table via SQL Editor or dashboard:
     ```sql
     CREATE TABLE batch_jobs (
         job_id SERIAL PRIMARY KEY,
         job_name TEXT NOT NULL,
         status TEXT DEFAULT 'RUNNING',  -- e.g., RUNNING, COMPLETED, FAILED
         start_time TIMESTAMP DEFAULT NOW(),
         end_time TIMESTAMP,
         error_msg TEXT
     );
     ```
   - Insert sample data for testing:
     ```sql
     INSERT INTO batch_jobs (job_name, status, error_msg) VALUES
     ('Backup Script', 'COMPLETED', NULL),
     ('Data Sync', 'FAILED', 'Connection Timeout'),
     ('Report Gen', 'RUNNING', NULL);
     ```

5. **Configure Environment**:
   - Create a `.env` file in the root:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_ANON_KEY=your_supabase_anon_key
     EMAIL_PASS=your_gmail_app_password  # Not plain password!
     ```
   - Add `.env` to `.gitignore` for security.

## ▶️ Running the App

1. **Start Streamlit**:
   ```
   streamlit run app.py  # Replace 'app.py' with your main script name
   ```

2. **Access the Dashboard**:
   - Opens at `http://localhost:8501`.
   - Use sidebar to navigate modules.

3. **Usage Tips**:
   - **Health Monitor**: Click "Send Alert if Critical" for emails.
   - **Log Analyzer**: Upload a CSV with columns like `timestamp`, `level`, `message`. Use regex for patterns.
   - **Service Manager**: On Linux, ensure sudo access for start/stop (run Streamlit with `sudo` if needed, but insecure—use policies). On Windows, input service names like "wuauserv".
   - **Batch Jobs/DB Alerts**: Data pulls from Supabase; refresh for updates.
   - **Logout/Refresh**: Clears session state.

## 📁 Project Structure

```
cloud_based_app_support_automationTool/
├── app.py               # Main Streamlit script
├── .env                 # Config (gitignore this!)
├── requirements.txt     # Pip dependencies (generate with pip freeze > requirements.txt)
└── README.md           # This file
```

## ⚠️ Limitations & Notes

- **Security**: Email uses basic SMTP—use OAuth2 for production. Sudo for services requires passwordless sudo or run as root (not recommended).
- **Platform Quirks**: 
  - Linux: Needs systemd (enable in WSL via `/etc/wsl.conf` if using WSL).
  - Windows: `systemd-cgls` fallback to `sc query`; no sudo equivalent.
- **Supabase**: Assumes public anon access—use RLS (Row Level Security) for prod.
- **Error Handling**: Basic try/except; expand for logging.
- **No Auth**: Add Streamlit secrets or Auth0 for user login.

## 🔧 Troubleshooting

- **Subprocess Errors**: Check OS (Win/Linux) and permissions. Test commands in terminal.
- **Supabase Connection**: Verify URL/key with `supabase.ping()` in a script.
- **Email Fails**: Confirm app password and less secure apps if needed (Gmail settings).
- **No Data**: Seed Supabase table with sample jobs.

## 🤝 Contributing

Fork, PR, or open issues! Focus on adding metrics, auth, or multi-DB support.

## 📄 License

MIT License—feel free to use/modify.

---

*Built with ❤️ for ProdOps automation. Questions? Open an issue or email unix_anand@outlook.com.*