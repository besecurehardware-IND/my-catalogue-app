import pandas as pd
import json

def update_admin_panel():
    try:
        # 1. Excel read karna
        # Is line ko replace karein
        df = pd.read_excel('catalog.xlsx', engine='openpyxl')
        
        # 2. GitHub Raw link setup (Aapki repository ke hisab se)
        base_url = "https://raw.githubusercontent.com/besecurehardware-IND/my-catalogue-app/main/images/"
        
        # 3. Image URL banana
        df['imageUrl'] = base_url + df['image_name'].astype(str)
        
        # 4. Filter: Sirf wahi dikhao jo 'Available' hain
        available_df = df[df['status'] == 'Available']
        
        # 5. JSON tyar karna
        final_data = available_df[['id', 'name', 'mrp', 'rate', 'imageUrl']].to_dict(orient='records')
        
        with open('data.json', 'w') as f:
            json.dump(final_data, f, indent=4)
            
        print("✅ Data tyar hai! Photos aur Stock update ho gaye.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_admin_panel()