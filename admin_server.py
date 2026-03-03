from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import os
import subprocess

app = Flask(__name__)
app.secret_key = "besecure_secret_key" # Session ke liye zaroori hai

UPLOAD_FOLDER = 'images'
EXCEL_FILE = 'catalog.xlsx'

# --- CONFIGURATION ---
ADMIN_USER = "mohit"
ADMIN_PASS = "secure123"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# CSS Styling (Professional Look)
UI_STYLE = '''
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
    h2 { color: #1a73e8; margin-top: 0; text-align: center; }
    input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
    .btn { width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: 600; }
    .btn:disabled { background: #ccc; }
    .status-msg { text-align: center; padding: 15px; margin-top: 15px; border-radius: 6px; display: none; }
    .success { background: #d4edda; color: #155724; display: block; }
    .error { background: #f8d7da; color: #721c24; display: block; }
</style>
'''

@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return f'''
    {UI_STYLE}
    <div class="card">
        <h2>BE SECURE LOGIN</h2>
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Admin ID" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" class="btn">Login</button>
        </form>
    </div>
    '''

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    return "❌ Invalid Credentials! <a href='/'>Try again</a>"

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('home'))
    return f'''
    {UI_STYLE}
    <div class="card" style="max-width: 500px;">
        <h2>Product Dashboard</h2>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="text" id="id" placeholder="Product ID (e.g. SSDP-001)" required>
            <input type="text" id="name" placeholder="Product Name" required>
            <input type="number" id="mrp" placeholder="MRP" required>
            <input type="number" id="rate" placeholder="Dealer Rate" required>
            <input type="file" id="image" accept="image/*" required>
            <button type="button" id="uploadBtn" onclick="uploadData()" class="btn">Upload & Sync App</button>
        </form>
        <div id="statusBox" class="status-msg"></div>
        <br><center><a href="/logout">Logout</a></center>
    </div>

    <script>
    function uploadData() {{
        const btn = document.getElementById('uploadBtn');
        const statusBox = document.getElementById('statusBox');
        
        btn.disabled = true;
        btn.innerHTML = 'Syncing to GitHub... ⏳';
        statusBox.className = 'status-msg';
        statusBox.innerHTML = '';

        const formData = new FormData();
        formData.append('id', document.getElementById('id').value);
        formData.append('name', document.getElementById('name').value);
        formData.append('mrp', document.getElementById('mrp').value);
        formData.append('rate', document.getElementById('rate').value);
        formData.append('image', document.getElementById('image').files[0]);

        fetch('/upload', {{ method: 'POST', body: formData }})
        .then(response => response.text())
        .then(data => {{
            btn.disabled = false;
            btn.innerHTML = 'Upload & Sync App';
            statusBox.className = 'status-msg success';
            statusBox.innerHTML = '✅ DONE! App Updated Successfully.';
            document.getElementById('uploadForm').reset();
        }})
        .catch(error => {{
            btn.disabled = false;
            btn.innerHTML = 'Upload & Sync App';
            statusBox.className = 'status-msg error';
            statusBox.innerHTML = '❌ Error: ' + error;
        }});
    }}
    </script>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    if 'logged_in' not in session: return "Unauthorized", 401
    
    item_id = request.form['id']
    name = request.form['name']
    mrp = request.form['mrp']
    rate = request.form['rate']
    file = request.files['image']
    
    img_name = file.filename
    file.save(os.path.join(UPLOAD_FOLDER, img_name))
    
    df = pd.read_excel(EXCEL_FILE)
    new_row = {'id': item_id, 'name': name, 'mrp': mrp, 'rate': rate, 'image_name': img_name, 'status': 'Available'}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    
    subprocess.run(["UpdateApp.bat"], shell=True)
    return "Success"

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5000)