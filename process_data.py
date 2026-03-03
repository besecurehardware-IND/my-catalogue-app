import pandas as pd
import json
import os

def process():
    df = pd.read_excel('catalog.xlsx')
    # Sirf 'Available' items dikhane ke liye
    df = df[df['status'] == 'Available']
    
    products = []
    for _, row in df.iterrows():
        products.append({
            "id": str(row['id']),
            "name": str(row['name']),
            "mrp": str(row['mrp']),
            "rate": str(row['rate']),
            "material": str(row.get('material', '')),
            "size": str(row.get('size', '')),
            "finish": str(row.get('finish', '')),
            "unit": str(row.get('unit', '')),
            "description": str(row.get('description', '')),
            "imageUrl": f"https://raw.githubusercontent.com/besecurehardware-IND/my-catalogue-app/master/images/{row['image_name']}",
            "status": str(row['status'])
        })
    
    with open('data.json', 'width') as f:
        json.dump(products, f, indent=4)

if __name__ == "__main__":
    process()