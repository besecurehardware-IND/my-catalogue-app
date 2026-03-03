from flask import Flask, render_template, request, redirect
import pandas as pd
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'images'
EXCEL_FILE = 'catalog.xlsx'

# Ensure images folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return '''
    <div style="font-family: Arial; padding: 20px;">
        <h2>BE SECURE - Item Upload Panel</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            ID: <input type="text" name="id" required><br><br>
            Name: <input type="text" name="name" required><br><br>
            MRP: <input type="text" name="mrp" required><br><br>
            Rate: <input type="text" name="rate" required><br><br>
            Image: <input type="file" name="image" accept="image/*" required><br><br>
            <input type="submit" value="Upload & Update GitHub" style="padding: 10px 20px; background: #4CAF50; color: white; border: none; cursor: pointer;">
        </form>
    </div>
    '''

@app.route('/upload', methods=['POST']) # Corrected: 'methods' instead of 'method'
def upload():
    try:
        # 1. Form Data lena
        item_id = request.form['id']
        name = request.form['name']
        mrp = request.form['mrp']
        rate = request.form['rate']
        file = request.files['image']
        
        # 2. Image save karna
        img_name = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, img_name))
        
        # 3. Excel update karna
        df = pd.read_excel(EXCEL_FILE)
        new_data = {'id': item_id, 'name': name, 'mrp': mrp, 'rate': rate, 'image_name': img_name, 'status': 'Available'}
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        
        # 4. GitHub par Push karna (Aapki Batch file wala kaam)
        subprocess.run(["UpdateApp.bat"], shell=True)
        
        return "✅ Success! Item added and GitHub updated. <a href='/'>Add another</a>"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    app.run(port=5000)