from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import os
import subprocess

app = Flask(__name__)
app.secret_key = "besecure_2026_key"

UPLOAD_FOLDER = 'images'
EXCEL_FILE = 'catalog.xlsx'
ADMIN_USER = "mohit"
ADMIN_PASS = "secure123"

# Agar images folder nahi hai toh banao
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)

# --- NEW: Agar Excel nahi hai toh Nayi Create karne ka function ---
def check_excel():
    if not os.path.exists(EXCEL_FILE):
        columns = ['id', 'name', 'mrp', 'rate', 'material', 'size', 'finish', 'unit', 'description', 'image_name', 'status']
        df = pd.DataFrame(columns=columns)
        df.to_excel(EXCEL_FILE, index=False)
        print("✅ Nayi catalog.xlsx file bana di gayi hai.")

# Design and Layout
UI_STYLE = '''
<style>
    body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 600px; }
    h2 { color: #1a73e8; text-align: center; border-bottom: 2px solid #eef0f2; padding-bottom: 10px; }
    input, select, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .btn { width: 100%; padding: 14px; background: #1a73e8; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; }
    .status { text-align: center; padding: 10px; margin-top: 15px; border-radius: 8px; display: none; font-weight: bold; }
</style>
'''

@app.route('/')
def home():
    if 'logged_in' in session: return redirect(url_for('dashboard'))
    return f'''{UI_STYLE}<div class="card"><h2>🔒 BE SECURE LOGIN</h2><form action="/login" method="post"><input type="text" name="u" placeholder="Admin ID" required><input type="password" name="p" placeholder="Password" required><button type="submit" class="btn">Login</button></form></div>'''

@app.route('/login', methods=['POST'])
def login():
    if request.form['u'] == ADMIN_USER and request.form['p'] == ADMIN_PASS:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    return "Invalid Credentials! <a href='/'>Back</a>"

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session: return redirect(url_for('home'))
    check_excel() # Har baar check karega Excel hai ya nahi
    return f'''{UI_STYLE}
    <div class="card">
        <h2>🛠️ PRODUCT DASHBOARD</h2>
        <form id="uForm">
            <div class="grid">
                <input type="text" id="id" placeholder="Product ID" required>
                <input type="text" id="name" placeholder="Name" required>
                <input type="number" id="mrp" placeholder="MRP" required>
                <input type="number" id="rate" placeholder="Dealer Rate" required>
                <input type="text" id="mat" placeholder="Material">
                <input type="text" id="size" placeholder="Size">
                <input type="text" id="fin" placeholder="Finish">
                <select id="unit"><option value="Per Pcs">Per Pcs</option><option value="Per Set">Per Set</option></select>
            </div>
            <textarea id="desc" placeholder="Product Description"></textarea>
            <input type="file" id="img" accept="image/*" required>
            <button type="button" id="btn" onclick="saveData()" class="btn">🚀 Upload & Sync to App</button>
        </form>
        <div id="msg" class="status"></div>
        <center><br><a href="/logout" style="color:red; text-decoration:none;">Logout Admin</a></center>
    </div>
    <script>
    function saveData() {{
        const b = document.getElementById('btn');
        const m = document.getElementById('msg');
        b.disabled = true; b.innerHTML = 'Updating App... Please Wait ⏳';
        
        const fd = new FormData();
        fd.append('id', document.getElementById('id').value);
        fd.append('name', document.getElementById('name').value);
        fd.append('mrp', document.getElementById('mrp').value);
        fd.append('rate', document.getElementById('rate').value);
        fd.append('material', document.getElementById('mat').value);
        fd.append('size', document.getElementById('size').value);
        fd.append('finish', document.getElementById('fin').value);
        fd.append('unit', document.getElementById('unit').value);
        fd.append('desc', document.getElementById('desc').value);
        fd.append('image', document.getElementById('img').files[0]);

        fetch('/upload', {{method:'POST', body:fd}})
        .then(r => r.text()).then(d => {{
            b.disabled = false; b.innerHTML = '🚀 Upload & Sync to App';
            m.style.display = 'block'; m.style.backgroundColor = '#d4edda'; m.style.color = '#155724';
            m.innerHTML = '✅ DONE! Item added and GitHub updated.';
            document.getElementById('uForm').reset();
            setTimeout(() => {{ m.style.display = 'none'; }}, 5000);
        }});
    }}
    </script>'''

@app.route('/upload', methods=['POST'])
def upload():
    if 'logged_in' not in session: return "Unauthorized", 401
    check_excel()
    f = request.form
    img = request.files['image']
    img.save(os.path.join(UPLOAD_FOLDER, img.filename))
    
    df = pd.read_excel(EXCEL_FILE)
    new_item = {
        'id': f['id'], 'name': f['name'], 'mrp': f['mrp'], 'rate': f['rate'],
        'material': f['material'], 'size': f['size'], 'finish': f['finish'],
        'unit': f['unit'], 'description': f['desc'], 'image_name': img.filename, 'status': 'Available'
    }
    df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    
    # Push to GitHub
    subprocess.run(["UpdateApp.bat"], shell=True)
    return "OK"

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5000)