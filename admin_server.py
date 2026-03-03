from flask import Flask, render_template, request, redirect
import pandas as pd
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'images'
EXCEL_FILE = 'catalog.xlsx'
ADMIN_PASSWORD = "secure123" # <--- Yahan apna password badal sakte hain

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>BE SECURE Admin</title>
        <script>
            function showLoading() {
                document.getElementById('uploadBtn').value = 'Updating GitHub... Please Wait ⏳';
                document.getElementById('uploadBtn').disabled = true;
                document.getElementById('uploadForm').submit();
            }
        </script>
    </head>
    <body style="font-family: sans-serif; background-color: #f4f4f9; padding: 40px;">
        <div style="max-width: 400px; margin: auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h2 style="color: #333; text-align: center;">BE SECURE Admin Panel</h2>
            <hr>
            <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data">
                <label>Admin Password:</label><br>
                <input type="password" name="password" required style="width:100%; margin-bottom:15px;"><br>
                
                <label>Item ID:</label><br>
                <input type="text" name="id" required style="width:100%; margin-bottom:15px;"><br>
                
                <label>Product Name:</label><br>
                <input type="text" name="name" required style="width:100%; margin-bottom:15px;"><br>
                
                <label>MRP:</label><br>
                <input type="number" name="mrp" required style="width:100%; margin-bottom:15px;"><br>
                
                <label>Your Rate:</label><br>
                <input type="number" name="rate" required style="width:100%; margin-bottom:15px;"><br>
                
                <label>Select Image:</label><br>
                <input type="file" name="image" accept="image/*" required style="width:100%; margin-bottom:20px;"><br>
                
                <input type="button" id="uploadBtn" value="Upload & Sync App" onclick="showLoading()" 
                       style="width:100%; padding: 12px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # 1. Password Check
        user_pass = request.form['password']
        if user_pass != ADMIN_PASSWORD:
            return "❌ Wrong Password! <a href='/'>Try again</a>"

        # 2. Form Data
        item_id = request.form['id']
        name = request.form['name']
        mrp = request.form['mrp']
        rate = request.form['rate']
        file = request.files['image']
        
        # 3. Save Image
        img_name = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, img_name))
        
        # 4. Update Excel
        df = pd.read_excel(EXCEL_FILE)
        new_row = {'id': item_id, 'name': name, 'mrp': mrp, 'rate': rate, 'image_name': img_name, 'status': 'Available'}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        
        # 5. Run GitHub Push
        print("Pushing to GitHub...")
        result = subprocess.run(["UpdateApp.bat"], shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return f"✅ SUCCESS! Item added and App updated.<br><pre>{result.stdout}</pre><br><a href='/'>Add Next Item</a>"
        else:
            return f"❌ GitHub Update Failed!<br><pre>{result.stderr}</pre><br><a href='/'>Back</a>"

    except Exception as e:
        return f"❌ System Error: {str(e)} <a href='/'>Back</a>"

if __name__ == '__main__':
    app.run(port=5000, debug=True)