from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import pandas as pd
import os
import threading
import subprocess
import time

app = Flask(__name__)
app.secret_key = "besecure_ultra_fast_2026"

# Folders Setup
UPLOAD_FOLDER = 'static/images'
EXCEL_FILE = 'catalog.xlsx'
ADMIN_USER = "mohit"
ADMIN_PASS = "secure123"

if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def fast_github_sync():
    """Background thread to push data to GitHub without freezing the UI"""
    try:
        # Step 1: Excel to JSON conversion (Instant)
        subprocess.run(["python", "process_data.py"], shell=True)
        # Step 2: GitHub Push (Takes time, but runs in background)
        subprocess.run(["UpdateApp.bat"], shell=True)
        print("✅ GitHub Sync Successful!")
    except Exception as e:
        print(f"❌ Sync Error: {e}")

UI_STYLE = '''
<style>
    :root { --primary: #2563eb; --dark: #0f172a; --bg: #f8fafc; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); margin: 0; display: flex; height: 100vh; overflow: hidden; }
    .sidebar { width: 280px; background: var(--dark); color: white; padding: 25px; display: flex; flex-direction: column; }
    .main { flex: 1; padding: 30px; overflow-y: auto; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 20px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
    input, select, textarea { width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
    .btn-fast { background: var(--primary); color: white; padding: 14px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; font-size: 16px; transition: 0.2s; }
    .btn-fast:hover { background: #1d4ed8; }
    .loader { display: none; color: #64748b; font-size: 12px; margin-top: 10px; text-align: center; }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; padding: 12px; background: #f1f5f9; position: sticky; top: 0; }
    td { padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
    .img-preview { width: 45px; height: 45px; object-fit: cover; border-radius: 6px; }
</style>
'''

@app.route('/')
def home():
    if 'logged_in' in session: return redirect(url_for('dashboard'))
    return f'''{UI_STYLE}<div style="display:flex; width:100%; height:100vh; align-items:center; justify-content:center; background:var(--dark);">
    <div class="card" style="width:350px; text-align:center;">
        <h2 style="margin-bottom:20px;">BE SECURE LOGIN</h2>
        <form action="/login" method="post"><input type="text" name="u" placeholder="Admin ID" required><br><br>
        <input type="password" name="p" placeholder="Password" required><br><br>
        <button class="btn-fast">ENTER DASHBOARD</button></form></div></div>'''

@app.route('/login', methods=['POST'])
def login():
    if request.form['u'] == ADMIN_USER and request.form['p'] == ADMIN_PASS:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    return "Failed! <a href='/'>Retry</a>"

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('home'))
    df = pd.read_excel(EXCEL_FILE) if os.path.exists(EXCEL_FILE) else pd.DataFrame()
    rows = ""
    for idx, item in df.iloc[::-1].head(10).iterrows(): # Sirf latest 10 dikhayega speed ke liye
        img = str(item.get('image_name', '')).split(',')[0]
        rows += f'<tr><td><img src="/static/images/{img}" class="img-preview" onerror="this.src=\'https://via.placeholder.com/45\'"></td><td><b>{item.get("id")}</b></td><td>{item.get("name")}</td><td>₹{item.get("rate")}</td><td><a href="/delete/{idx}" style="color:red;text-decoration:none;">X</a></td></tr>'

    return f'''{UI_STYLE}
    <div class="sidebar">
        <h2>BE SECURE PRO</h2><hr style="border:0.5px solid #334155; width:100%;">
        <p>Total Inventory: {len(df)} Items</p>
        <div style="margin-top:auto;"><a href="/logout" style="color:#94a3b8; text-decoration:none;">Logout</a></div>
    </div>
    <div class="main">
        <div class="card">
            <h3>⚡ Instant Product Add</h3>
            <form id="fastForm">
                <div class="grid">
                    <input type="text" id="id" placeholder="Product ID" required>
                    <input type="text" id="name" placeholder="Name" required>
                    <input type="number" id="rate" placeholder="Rate" required>
                    <input type="text" id="mat" placeholder="Material">
                    <input type="text" id="size" placeholder="Size">
                    <input type="text" id="fin" placeholder="Finish">
                </div>
                <input type="file" id="imgs" multiple style="margin-top:15px; border:none;">
                <button type="button" onclick="instantSave()" class="btn-fast" style="margin-top:15px;">⚡ QUICK SAVE & SYNC</button>
                <div id="ld" class="loader">Saving to Local Excel... Done! Syncing to Cloud in background...</div>
            </form>
        </div>
        <div class="card">
            <h3>Recent Items</h3>
            <table><tr><th>Image</th><th>ID</th><th>Name</th><th>Rate</th><th>Action</th></tr>{rows}</table>
        </div>
    </div>
    <script>
    function instantSave() {{
        const fd = new FormData();
        const btn = event.target;
        document.getElementById('ld').style.display = 'block';
        btn.disabled = true;

        fd.append('id', document.getElementById('id').value);
        fd.append('name', document.getElementById('name').value);
        fd.append('rate', document.getElementById('rate').value);
        fd.append('material', document.getElementById('mat').value);
        fd.append('size', document.getElementById('size').value);
        fd.append('finish', document.getElementById('fin').value);
        const files = document.getElementById('imgs').files;
        for (let i = 0; i < files.length; i++) {{ fd.append('images', files[i]); }}

        fetch('/upload', {{method:'POST', body:fd}}).then(() => {{
            location.reload(); // Turant refresh hoga, bina github ka wait kiye
        }});
    }}
    </script>'''

@app.route('/upload', methods=['POST'])
def upload():
    f = request.form
    files = request.files.getlist('images')
    img_names = [file.filename for file in files]
    for file in files: file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    
    # 1. Excel Update (Instant)
    df = pd.read_excel(EXCEL_FILE) if os.path.exists(EXCEL_FILE) else pd.DataFrame()
    new_data = {'id': f['id'], 'name': f['name'], 'rate': f['rate'], 'image_name': ",".join(img_names)}
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    # 2. GitHub Sync (Background Thread - NO WAITING)
    threading.Thread(target=fast_github_sync).start()
    
    return "OK"

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5000, debug=False)