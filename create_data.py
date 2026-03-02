import pandas as pd
import os

# Data folder check karna
if not os.path.exists('data'):
    os.makedirs('data')

# Sample Product Data
data = {
    'Item_ID': ['H001', 'H002', 'M010', 'P005', 'G009'],
    'Product_Name': ['Antique Brass Handle', 'Luxury Rose Gold Pull', 'MOP Inlay Handle', 'Pooja Mandir Knob', 'Crystal Glass Handle'],
    'Category': ['Door Handles', 'Premium', 'Mother of Pearl', 'Religious', 'Glass Series'],
    'MRP': [1500, 2800, 5500, 450, 3200],
    'Dealer_Rate': [950, 1900, 4200, 300, 2100],
    'Stock_Status': ['Available', 'Limited', 'Available', 'Out of Stock', 'Available']
}

df = pd.DataFrame(data)
df.to_excel('data/products.xlsx', index=False)
print("✅ Excel file 'data/products.xlsx' ban gayi hai!")