import streamlit as st
import pandas as pd
import os

# 1. Page Config (Sabse upar hona chahiye)
st.set_page_config(page_title="Dealer Digital Catalogue", layout="wide")

# 2. Login Logic
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔐 Dealer Login")
    password = st.text_input("Access Password Daalein", type="password")
    if st.button("Login"):
        if password == "1234":
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.error("Galat Password!")
    st.stop()

# 3. Main App (Login ke baad dikhega)
st.title("📦 Digital Catalogue")

try:
    # Excel file load karna
    df = pd.read_excel("data/products.xlsx")
    
    # Search Bar
    search = st.sidebar.text_input("Product Search Karein...")
    
    # Filtering
    if search:
        df = df[df['Product_Name'].str.contains(search, case=False) | 
                df['Item_ID'].str.contains(search, case=False)]

    # Product Grid Display
    for index, row in df.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            
            # Photo Check
            img_name = f"images/{row['Item_ID']}.jpg"
            with col1:
                if os.path.exists(img_name):
                    st.image(img_name, width=200)
                else:
                    st.write("📷 Photo Not Found")
            
            # Details
            with col2:
                st.subheader(row['Product_Name'])
                st.write(f"**Item ID:** {row['Item_ID']}")
                st.write(f"**Category:** {row['Category']}")
                
                # Pricing
                c1, c2 = st.columns(2)
                c1.metric("MRP", f"₹{row['MRP']}")
                c2.metric("Dealer Rate", f"₹{row['Dealer_Rate']}")
                
                st.info(f"Stock Status: {row['Stock_Status']}")

except Exception as e:
    st.error(f"Error: {e}. 'data/products.xlsx' file check karein.")

# Logout Button
if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.rerun()
