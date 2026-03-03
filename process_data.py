import pandas as pd
import json
import datetime

def process():
    df = pd.read_excel('catalog.xlsx')
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
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    with open('data.json', 'w') as f:
        json.dump(products, f, indent=4)
    print("✅ data.json updated with timestamp!")

if __name__ == "__main__":
    process()