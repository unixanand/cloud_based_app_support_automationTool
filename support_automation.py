import streamlit as st
import psutil
import subprocess
import platform
import pandas as pd
import re
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import smtplib
from email.mime.text import MIMEText
from datetime import date, timedelta

load_dotenv()  # Load .env

# Supabase Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Email Config
EMAIL_FROM = "unixanand2005@gmail.com"
EMAIL_TO = "unix_anand@outlook.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

st.markdown("""
<style>
.stButton>button {
    background-color: #8b4513;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="ProdOps Dashboard (Supabase Direct)", layout="wide")
st.title("⚙️️ Production Support Automation Dashboard")

# Sidebar navigation
page = st.sidebar.selectbox("Choose Module", ["Health Monitor", "Log Analyzer", "Service Manager", "Batch Jobs", "DB Alerts", "Batch Manager"])
if st.sidebar.button("Refresh"):
    st.session_state.clear()
    st.rerun()
        
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.header("Logging out!")
    st.stop()

if page == "Health Monitor":
    col1, col2, col3, col4 = st.columns(4)
    cpu = psutil.cpu_percent()
    with col1: st.metric("CPU %", cpu)
    with col2: st.metric("Memory %", psutil.virtual_memory().percent)
    with col3: st.metric("Disk %", psutil.disk_usage('/').percent)
    with col4: st.metric("Network Sent", f"{psutil.net_io_counters().bytes_sent / 1024**2:.1f}", "MB")
    
    if cpu > 80:
        st.warning("High CPU Detected!")
    if st.button("Send Alert if Critical"):
        if cpu > 80:
            msg = MIMEText(f"High CPU Alert: {cpu}% on PROD APP Server")
            #msg = MIMEText(f"High CPU Alert: {cpu}% on {os.uname().nodename}")
            msg['Subject'] = 'Prod Health Alert'
            msg['From'] = EMAIL_FROM
            msg['To'] = EMAIL_TO
            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(EMAIL_FROM, os.getenv("EMAIL_PASS", "your_app_pass"))
                    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
                st.success("Alert Emailed!")
            except Exception as e:
                st.error(f"Email Error: {e}")

elif page == "Log Analyzer":
    uploaded_file = st.file_uploader("Upload Log File (CSV/TSV; cols: timestamp, level, message)")
    #pattern = st.text_input("Grep Pattern (e.g., ERROR|FAIL)", value="ERROR")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        if 'message' not in df.columns:
            st.error("CSV must have 'message' column for grep.")
        else:
            # Grep-like filter
            col1, col2, col3 = st.columns([2, 0.5, 0.5])
            with col1:
                pattern = st.text_input("Grep Pattern (e.g., ERROR|FAIL)", value="ERROR")
            with col3:
                st.write("Search Pattern")
                search = st.button("Search")
            if search:
                mask = df['message'].str.contains(pattern, case=False, na=False, regex=True)
                filtered = df[mask]
                st.dataframe(filtered)
                if not filtered.empty and 'timestamp' in filtered.columns:
                    st.bar_chart(pd.to_datetime(filtered['timestamp']).dt.floor('H').value_counts().sort_index())
                else:
                    st.info("No timestamp column for charting.")

elif page == "Service Manager":
    service = ""
    if platform.system() == "Windows":
        # Windows equivalent: sc query <service>
        cmd = ["sc", "query", service]
        service_list = ["sc", "query"]
    else:
        # Linux: systemctl status <service>
        cmd = ["systemctl", "status", service]
        
    tab1, tab2 = st.tabs(["Service List","Start/Stop Services"])
    with tab1:
        result = subprocess.run(service_list, capture_output=True, text=True, timeout=10)
        st.code(result.stdout, language="bash")
    
    with tab2:                     
            service = st.text_input("Service Name (e.g., postgresql)")
            if st.button("Status"):
                try:
                    #cmd = ["sc", "query", service]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    #result = subprocess.run(["systemctl", "status", service], capture_output=True, text=True, timeout=10)
                    st.code(result.stdout, language="bash")
                    if result.returncode != 0:
                        st.error("Service Issue Detected")
                except subprocess.TimeoutExpired:
                    st.warning("Command Timed Out")
    
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Start"):
                    try:
                        subprocess.run(["sudo", "systemctl", "start", service], check=True)
                        st.success("Service Started!")
                    except subprocess.CalledProcessError as e:
                        st.error(f"Failed to start: {e} (Check sudo access)")
                    st.rerun()
            with col2:
                if st.button("Stop"):
                    try:
                        subprocess.run(["sudo", "systemctl", "stop", service], check=True)
                        st.success("Service Stopped!")
                    except subprocess.CalledProcessError as e:
                        st.error(f"Failed to stop: {e} (Check sudo access)")
                    st.rerun()
            with col3:
                if st.button("Restart"):
                    try:
                        subprocess.run(["sudo", "systemctl", "restart", service], check=True)
                        st.success("Service Restarted!")
                    except subprocess.CalledProcessError as e:
                        st.error(f"Failed to restart: {e} (Check sudo access)")
                    st.rerun()

elif page == "Batch Jobs":
    try:
        # Fetch recent jobs
        response = (
            supabase.table("batch_jobs")
            .select("*")
            .order("start_time", desc=True)
            .limit(50)
            .execute()
        )
        jobs_data = response.data
        jobs = pd.DataFrame(jobs_data) if jobs_data else pd.DataFrame()
        
        #st.dataframe(jobs, use_container_width=True)
        st.dataframe(jobs, width='stretch')
        
        if not jobs.empty:
            failures = jobs[jobs['status'] == 'FAILED']
            
            if not failures.empty:
                st.error(f"{len(failures)} Recent Failures")
                st.dataframe(failures[['job_name', 'error_msg', 'end_time']])
                if st.button("Retry Failures"):
                    # Placeholder: Update status to 'RUNNING' for failures
                    for idx, row in failures.iterrows():
                        supabase.table("batch_jobs").update({"status": "RUNNING"}).eq("job_id", row['job_id']).execute()
                    st.success("Failures Marked for Retry – Refresh to Check!")
                    st.rerun()
    except Exception as e:
        st.error(f"Query Error: {e}")

elif page == "DB Alerts":
    try:
        # Simplified: Job stats as proxy for DB health (e.g., failure trends)
        recent_fails = False
        response = supabase.table("batch_jobs").select("status").execute()
        stats = pd.DataFrame(response.data).groupby('status').size().reset_index(name='count')
        st.subheader("Batch Job Health Summary")
        st.dataframe(stats)

        yesterday = date.today() - timedelta(days=1)
        col1, col2, col3 = st.columns(3)
        with col1:
            scan = st.button("Scan for Issues")
        with col3:
            sendmsg = st.button("Notify Email")
        if scan:
            # Check recent failures
            fail_response = (
                supabase.table("batch_jobs")
                .select("*")
                .eq("status", "FAILED")
                .gte("start_time", yesterday)
                .execute()
            )
            recent_fails = fail_response.data
            if recent_fails:
                st.warning(f"{len(recent_fails)} Failures in Last 24h")
                st.json(recent_fails)  # Or pd.DataFrame(recent_fails)
            else:
                st.success("No Recent Issues")
        if sendmsg:
            if recent_fails:
        
                msg = MIMEText(f"High Failure Alert: on PROD Batch Jobs")
                #msg = MIMEText(f"High CPU Alert: {cpu}% on {os.uname().nodename}")
                msg['Subject'] = 'Prod Batch Alert'
                msg['From'] = EMAIL_FROM
                msg['To'] = EMAIL_TO
                try:
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(EMAIL_FROM, os.getenv("EMAIL_PASS", "your_app_pass"))
                        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
                    st.success("Alert Emailed!")
                except Exception as e:
                    st.error(f"Email Error: {e}")
                
        # Threshold example: High failure rate
        total_jobs = len(response.data) if response.data else 0
        fail_count = len([j for j in response.data if j.get('status') == 'FAILED'])
        fail_rate = (fail_count / total_jobs * 100) if total_jobs > 0 else 0
        if fail_rate > 20:
            st.warning(f"High Failure Rate: {fail_rate:.1f}% – Investigate!")
    except Exception as e:
        st.error(f"Alert Error: {e}")

if page == "Batch Manager":
    st.header("Batch Manager Console")
# Footer
st.sidebar.markdown("---")
st.sidebar.info("Dashboard powered by Streamlit + Direct Supabase DB")
