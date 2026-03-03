from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import pandas as pd
import os
import threading
import subprocess

app = Flask(__name__)
app.secret_key = "besecure_superfast_2026"

# Folder Structure
UPLOAD_FOLDER = 'static/images'
EXCEL_FILE = 'catalog.xlsx'
ADMIN_USER = "mohit"
ADMIN_PASS = "secure123"

CATEGORIES = ["Mortise Handle", "Cabinet Handle", "Main Door Handle", "Pooja Mandir Handle", "Knobs", "Accessories"]

# Folders check
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_excel():
    if not os.path.exists(EXCEL_FILE):
        columns = ['id', 'name', 'category', 'mrp', 'rate', 'material', 'size', 'finish', 'unit', 'description', 'image_name', 'status']
        pd.DataFrame(columns=columns).to_excel(EXCEL_FILE, index=False)

def background_sync():
    """GitHub Push process in background"""
    print("🚀 Background Sync Started...")
    subprocess.run(["python", "process_data.py"], shell=True)
    subprocess.run(["UpdateApp.bat"], shell=True)
    print("✅ Background Sync Finished!")

UI_STYLE = '''
<style>
    :root { --primary: #2563eb; --success: #16a34a; --bg: #f1f5f9; }
    body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; display: flex; overflow: hidden; }
    .sidebar { width: 260px; background: #1e293b; color: white; height: 100vh; padding: 25px; box-sizing: border-box; }
    .main-content { flex: 1; height: 100vh; overflow-y: auto; padding: 30px; box-sizing: border-box; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
    input, select, textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; }
    .btn { padding: 12px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; transition: 0.2s; color: white; }
    .btn-save { background: var(--primary); width: 100%; }
    .btn-sync { background: var(--success); width: 100%; margin-top: 15px; font-size: 15px; }
    .btn-delete { background: #ef4444; padding: 5px 10px; font-size: 12px; color:white; text-decoration:none; border-radius:4px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th { background: #f8fafc; text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; }
    td { padding: 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
    .img-thumb { width: 45px; height: 45px; object-fit: cover; border-radius: 6px; }
    #syncMsg { font-size: 12px; text-align: center; margin-top: 8px; color: #94a3b8; }
</style>
'''

@app.route('/')
def home():
    if 'logged_in' in session: return redirect(url_for('dashboard'))
    return f'''{UI_STYLE}<div style="display:flex; width:100%; height:100vh; align-items:center; justify-content:center;">
    <div class="card" style="width:360px;"><h2>🔒 Admin Login</h2><form action="/login" method="post">
    <input type="text" name="u" placeholder="Username" required><br><br>
    <input type="password" name="p" placeholder="Password" required><br><br>
    <button class="btn btn-save">Login</button></form></div></div>'''

@app.route('/login', methods=['POST'])
def login():
    if request.form['u'] == ADMIN_USER and request.form['p'] == ADMIN_PASS:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    return "Invalid! <a href='/'>Retry</a>"

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('home'))
    check_excel()
    df = pd.read_excel(EXCEL_FILE)
    rows = ""
    for idx, item in df.iloc[::-1].iterrows():
        img_str = str(item.get('image_name', ''))
        img = img_str.split(',')[0] if img_str else ""
        rows += f'''<tr>
            <td><img src="/static/images/{img}" class="img-thumb" onerror="this.src='https://via.placeholder.com/45'"></td>
            <td>{item.get('id')}</td>
            <td>{item.get('name')}</td>
            <td>{item.get('category')}</td>
            <td>₹{item.get('rate')}</td>
            <td><a href="/delete/{idx}" class="btn-delete" onclick="return confirm('Pakka delete karein?')">X</a></td>
        </tr>'''

    cat_options = "".join([f'<option value="{c}">{c}</option>' for c in CATEGORIES])

    return f'''{UI_STYLE}
    <div class="sidebar">
        <h2>BeSecure Pro</h2><hr style="border:0.5px solid #334155">
        <p>📦 Items: {len(df)}</p>
        <button class="btn btn-sync" onclick="startSync()">🔄 LIVE SYNC TO APP</button>
        <div id="syncMsg"></div>
        <br><br><a href="/logout" style="color:#94a3b8; text-decoration:none;">Sign Out</a>
    </div>
    <div class="main-content">
        <div class="card">
            <h3>⚡ Quick Add Product</h3>
            <form id="productForm">
                <div class="grid">
                    <input type="text" id="id" placeholder="Product ID" required>
                    <input type="text" id="name" placeholder="Product Name" required>
                    <select id="cat">{cat_options}</select>
                    <input type="number" id="mrp" placeholder="MRP">
                    <input type="number" id="rate" placeholder="Dealer Rate" required>
                    <input type="text" id="mat" placeholder="Material">
                    <input type="text" id="size" placeholder="Size">
                    <input type="text" id="fin" placeholder="Finish">
                    <select id="unit"><option value="Per Pcs">Per Pcs</option><option value="Per Set">Per Set</option></select>
                </div>
                <textarea id="desc" placeholder="Product Description" style="margin-top:10px; height:60px;"></textarea>
                <div style="margin-top:10px;">
                    <label style="font-size:12px; color:#64748b;">Select Images (Multiple):</label>
                    <input type="file" id="imgs" multiple required>
                </div>
                <button type="button" onclick="saveItem()" class="btn btn-save" style="margin-top:15px;">⚡ QUICK SAVE (INSTANT)</button>
            </form>
        </div>
        <div class="card">
            <h3>Recent Inventory</h3>
            <table>
                <tr><th>Image</th><th>ID</th><th>Name</th><th>Category</th><th>Rate</th><th>Action</th></tr>
                {rows}
            </table>
        </div>
    </div>
    <script>
    function saveItem() {{
        const btn = event.target; btn.innerText = "Saving..."; btn.disabled = true;
        const fd = new FormData();
        fd.append('id', document.getElementById('id').value);
        fd.append('name', document.getElementById('name').value);
        fd.append('category', document.getElementById('cat').value);
        fd.append('mrp', document.getElementById('mrp').value || 0);
        fd.append('rate', document.getElementById('rate').value);
        fd.append('material', document.getElementById('mat').value || "");
        fd.append('size', document.getElementById('size').value || "");
        fd.append('finish', document.getElementById('fin').value || "");
        fd.append('unit', document.getElementById('unit').value);
        fd.append('desc', document.getElementById('desc').value || "");
        const files = document.getElementById('imgs').files;
        for (let i = 0; i < files.length; i++) {{ fd.append('images', files[i]); }}

        fetch('/upload', {{method:'POST', body:fd}}).then(() => location.reload());
    }}
    function startSync() {{
        document.getElementById('syncMsg').innerText = "Syncing in background... ⏳";
        fetch('/sync').then(() => {{
            document.getElementById('syncMsg').innerText = "✅ Sync process started!";
            setTimeout(() => document.getElementById('syncMsg').innerText = "", 5000);
        }});
    }}
    </script>'''

@app.route('/upload', methods=['POST'])
def upload():
    check_excel()
    f = request.form
    files = request.files.getlist('images')
    img_names = []
    for file in files:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        img_names.append(file.filename)
    
    df = pd.read_excel(EXCEL_FILE)
    new_item = {
        'id': f['id'], 'name': f['name'], 'category': f['category'], 'mrp': f['mrp'], 
        'rate': f['rate'], 'material': f['material'], 'size': f['size'], 
        'finish': f['finish'], 'unit': f['unit'], 'description': f['desc'], 
        'image_name': ",".join(img_names), 'status': 'Available'
    }
    df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    
    # Auto-Sync Trigger
    thread = threading.Thread(target=background_sync)
    thread.start()
    return "OK"

@app.route('/sync')
def sync():
    thread = threading.Thread(target=background_sync)
    thread.start()
    return "Syncing"

@app.route('/delete/<int:idx>')
def delete_item(idx):
    df = pd.read_excel(EXCEL_FILE)
    df = df.drop(idx)
    df.to_excel(EXCEL_FILE, index=False)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5000)