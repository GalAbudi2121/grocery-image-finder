import streamlit as st
import requests
import os

# --- CONFIGURATION ---
# Use the same keys you used before
API_KEY = st.secrets["GOOGLE_API_KEY"]
CX = st.secrets["GOOGLE_CX"]

st.set_page_config(page_title="Product Image Finder", page_icon="🛒")

st.title("🛒 מכולת - מוצא תמונות מוצרים")
st.write("Enter the details below to find official product images.")

# --- UI INPUTS ---
col1, col2 = st.columns(2)
with col1:
    product = st.text_input("Product Name (שם מוצר):", placeholder="קוטג' 5 אחוז")
with col2:
    manufacturer = st.text_input("Manufacturer (יצרן):", placeholder="תנובה")

num_results = st.slider("How many images?", 1, 5, 3)

if st.button("Search Images"):
    if not API_KEY or not CX:
        st.error("Missing API Key or CX ID!")
    elif product and manufacturer:
        query = f"{manufacturer} {product} official product image"
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query,
            "searchType": "image",
            "num": num_results,
            "safe": "active"
        }

        with st.spinner('Searching Google...'):
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                if items:
                    st.success(f"Found {len(items)} images!")
                    for item in items:
                        st.subheader(item['title'])
                        # This displays the image directly in the browser
                        st.image(item['link'], use_container_width=True)
                        st.caption(f"Source: {item['image']['contextLink']}")
                        st.divider()
                else:
                    st.warning("No images found.")
            else:
                st.error(f"Error: {response.status_code}")
                st.json(response.json())
    else:

        st.info("Please enter both product name and manufacturer.")
