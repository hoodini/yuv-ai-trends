# Example: Automate with Windows Task Scheduler

This guide shows you how to automate the Gen AI News Aggregator on Windows.

## Option 1: Windows Task Scheduler (GUI)

1. Open Task Scheduler (search in Start menu)
2. Click "Create Basic Task"
3. Name it: "Gen AI News Daily Digest"
4. Trigger: Daily at your preferred time (e.g., 8:00 AM)
5. Action: Start a program
6. Program/script: `powershell.exe`
7. Add arguments: `-Command "cd 'C:\Users\User\Documents\projects\news'; python main.py --range daily --open"`
8. Finish

## Option 2: PowerShell Script

Create a file `run_digest.ps1`:

```powershell
# Navigate to project directory
Set-Location "C:\Users\User\Documents\projects\news"

# Activate virtual environment if you're using one
# .\venv\Scripts\Activate.ps1

# Run the aggregator
python main.py --range daily --open

# Optional: Send email or notification
# Add your notification logic here
```

Then schedule this script using Task Scheduler.

## Option 3: Quick PowerShell Command

Run this once to set up a scheduled task via PowerShell:

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command `"cd 'C:\Users\User\Documents\projects\news'; python main.py --range daily`""
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "GenAINewsDaily" -Description "Daily Gen AI news digest"
```

## Customization Ideas

### Weekly Summary (Mondays at 9 AM)
```powershell
python main.py --range weekly --output weekly_summary.html --open
```

### Monthly Report (First day of month)
```powershell
python main.py --range monthly --output monthly_report.html
```

### Custom 3-day digest
```powershell
python main.py --days 3 --open
```

## Email Integration

To email the digest, you can extend the script:

```python
# Add to main.py or create separate script
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_digest_email(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Configure your email settings
    sender = "your-email@gmail.com"
    receiver = "your-email@gmail.com"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Gen AI News Digest - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = sender
    msg['To'] = receiver
    
    msg.attach(MIMEText(html_content, 'html'))
    
    # Send via Gmail (requires app password)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, "your-app-password")
        server.sendmail(sender, receiver, msg.as_string())
```
