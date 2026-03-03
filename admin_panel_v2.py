from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import pandas as pd
import os
import threading
import subprocess

app = Flask(__name__)
app.secret_key = "besecure_superfast_2026"

UPLOAD_FOLDER = 'static/images'
EXCEL_FILE = 'catalog.xlsx'
ADMIN_USER = "mohit"
ADMIN_PASS = "secure123"

CATEGORIES = ["Mortise Handle", "Cabinet Handle", "Main Door Handle", "Pooja Mandir Handle", "Knobs", "Accessories"]

if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_excel():
    if not os.path.exists(EXCEL_FILE):
        columns = ['id', 'name', 'category', 'mrp', 'rate', 'material', 'size', 'finish', 'unit', 'description', 'image_name', 'status']
        pd.DataFrame(columns=columns).to_excel(EXCEL_FILE, index=False)

def background_sync():
    subprocess.run(["python", "process_data.py"], shell=True)
    subprocess.run(["UpdateApp.bat"], shell=True)

UI_STYLE = '''
<style>
    :root { --primary: #2563eb; --success: #16a34a; --bg: #f1f5f9; }
    body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; display: flex; }
    .sidebar { width: 260px; background: #1e293b; color: white; height: 100vh; padding: 25px; position: fixed; }
    .main-content { margin-left: 260px; flex: 1; padding: 30px; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
    input, select, textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; }
    .btn { padding: 12px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; color: white; }
    .btn-save { background: var(--primary); width: 100%; }
    .btn-edit { background: #f59e0b; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px; margin-right: 5px; }
    .btn-delete { background: #ef4444; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: left; font-size: 14px; }
    .img-thumb { width: 45px; height: 45px; object-fit: cover; border-radius: 6px; }
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
        img = str(item.get('image_name', '')).split(',')[0]
        # Edit function ko data pass karne ke liye logic
        item_json = jsonify(item.to_dict()).get_data(as_text=True).replace("'", "\\'")
        rows += f'''<tr>
            <td><img src="/static/images/{img}" class="img-thumb" onerror="this.src='https://via.placeholder.com/45'"></td>
            <td>{item.get('id')}</td>
            <td>{item.get('name')}</td>
            <td>₹{item.get('rate')}</td>
            <td>
                <button onclick='editItem({idx}, {item_json})' class="btn-edit">Edit</button>
                <a href="/delete/{idx}" class="btn-delete" onclick="return confirm('Delete karein?')">X</a>
            </td>
        </tr>'''

    return f'''{UI_STYLE}
    <div class="sidebar">
        <h2>BeSecure Pro</h2><hr>
        <p>📦 Total Items: {len(df)}</p>
        <a href="/logout" style="color:#94a3b8; text-decoration:none;">Sign Out</a>
    </div>
    <div class="main-content">
        <div class="card">
            <h3 id="formTitle">⚡ Add New Product</h3>
            <form id="productForm">
                <input type="hidden" id="edit_idx" value="-1">
                <div class="grid">
                    <input type="text" id="id" placeholder="Product ID" required>
                    <input type="text" id="name" placeholder="Product Name" required>
                    <select id="cat">{"".join([f'<option value="{c}">{c}</option>' for c in CATEGORIES])}</select>
                    <input type="number" id="mrp" placeholder="MRP">
                    <input type="number" id="rate" placeholder="Dealer Rate" required>
                    <input type="text" id="mat" placeholder="Material">
                    <input type="text" id="size" placeholder="Size">
                    <input type="text" id="fin" placeholder="Finish">
                    <select id="unit"><option value="Per Pcs">Per Pcs</option><option value="Per Set">Per Set</option></select>
                </div>
                <textarea id="desc" placeholder="Product Description" style="margin-top:10px; height:60px;"></textarea>
                <div style="margin-top:10px;">
                    <input type="file" id="imgs" multiple>
                    <p style="font-size:10px; color:gray;">(Edit ke waqt images select na karein agar wahi purani rakhni hain)</p>
                </div>
                <button type="button" id="submitBtn" onclick="saveItem()" class="btn btn-save" style="margin-top:15px;">⚡ SAVE PRODUCT</button>
            </form>
        </div>
        <div class="card">
            <h3>Recent Inventory</h3>
            <table>
                <tr><th>Image</th><th>ID</th><th>Name</th><th>Rate</th><th>Action</th></tr>
                {rows}
            </table>
        </div>
    </div>
    <script>
    function editItem(idx, data) {{
        document.getElementById('formTitle').innerText = "📝 Edit Product: " + data.name;
        document.getElementById('submitBtn').innerText = "🔄 UPDATE PRODUCT";
        document.getElementById('edit_idx').value = idx;
        document.getElementById('id').value = data.id;
        document.getElementById('name').value = data.name;
        document.getElementById('cat').value = data.category;
        document.getElementById('mrp').value = data.mrp;
        document.getElementById('rate').value = data.rate;
        document.getElementById('mat').value = data.material;
        document.getElementById('size').value = data.size;
        document.getElementById('fin').value = data.finish;
        document.getElementById('unit').value = data.unit;
        document.getElementById('desc').value = data.description;
        window.scrollTo(0,0);
    }}

    function saveItem() {{
        const fd = new FormData();
        fd.append('edit_idx', document.getElementById('edit_idx').value);
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
    </script>'''

@app.route('/upload', methods=['POST'])
def upload():
    check_excel()
    f = request.form
    idx = int(f.get('edit_idx', -1))
    df = pd.read_excel(EXCEL_FILE)
    
    # Image handling
    files = request.files.getlist('images')
    img_names = []
    if files and files[0].filename != '':
        for file in files:
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            img_names.append(file.filename)
        new_img_str = ",".join(img_names)
    else:
        # Edit ke waqt agar naye image nahi chunni toh purani wali hi rahegi
        new_img_str = df.at[idx, 'image_name'] if idx != -1 else ""

    item_data = {
        'id': f['id'], 'name': f['name'], 'category': f['category'], 'mrp': f['mrp'], 
        'rate': f['rate'], 'material': f['material'], 'size': f['size'], 
        'finish': f['finish'], 'unit': f['unit'], 'description': f['desc'], 
        'image_name': new_img_str, 'status': 'Available'
    }

    if idx != -1:
        # Update existing row
        for key, value in item_data.items():
            df.at[idx, key] = value
    else:
        # Add new row
        df = pd.concat([df, pd.DataFrame([item_data])], ignore_index=True)
    
    df.to_excel(EXCEL_FILE, index=False)
    
    # Auto-Sync in background
    thread = threading.Thread(target=background_sync)
    thread.start()
    return "OK"

@app.route('/delete/<int:idx>')
def delete_item(idx):
    df = pd.read_excel(EXCEL_FILE)
    df = df.drop(idx)
    df.to_excel(EXCEL_FILE, index=False)
    thread = threading.Thread(target=background_sync)
    thread.start()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5000)