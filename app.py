import streamlit as st
import requests
from io import BytesIO

# --- הגדרות שרת (Secrets) ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    CX = st.secrets["GOOGLE_CX"]
except:
    st.error("שגיאה: מפתחות ה-API לא הוגדרו ב-Secrets.")
    st.stop()

# עיצוב דף האפליקציה
st.set_page_config(page_title="חיפוש תמונות מוצר", page_icon="🛒")

# עיצוב לעברית (RTL)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    div[data-baseweb="input"] { direction: rtl; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 חיפוש תמונות מוצר נקיות")
st.write("הכנס שם מוצר למציאת תמונות איכותיות:")

# --- קלט מהמשתמש ---
product = st.text_input("שם המוצר:", placeholder="לדוגמה: מטרנה שלב 1")
manufacturer = st.text_input("שם היצרן (אופציונלי):")

if st.button("מצא תמונה"):
    if product:
        exclude_sites = "-site:amazon.* -site:youtube.com -site:pinterest.* -site:shutterstock.com -site:zap.co.il"
        clean_keywords = "צילום מוצר רקע לבן product white background"
        query = f"{manufacturer} {product} {clean_keywords} {exclude_sites}"
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query,
            "searchType": "image",
            "num": 5,
            "safe": "active",
            "imgSize": "large"
        }

        with st.spinner('מחפש ומוריד תמונות לתצוגה...'):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                if items:
                    for i, item in enumerate(items):
                        img_url = item['link']
                        
                        try:
                            # הורדת התמונה לזיכרון (זה פותר את השגיאה שקיבלת)
                            img_response = requests.get(img_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                            if img_response.status_code == 200:
                                img_bytes = BytesIO(img_response.content)
                                
                                # הצגת התמונה מהזיכרון
                                st.info(f"מקור: {item['displayLink']}")
                                st.image(img_bytes, use_container_width=True)
                                
                                # כפתור הורדה
                                st.download_button(
                                    label="💾 שמור תמונה זו",
                                    data=img_response.content,
                                    file_name=f"{product.replace(' ', '_')}_{i}.jpg",
                                    mime="image/jpeg",
                                    key=f"btn_{i}"
                                )
                                st.divider()
                        except Exception as e:
                            # אם תמונה ספציפית עדיין נחסמת, פשוט נדלג עליה
                            continue
                else:
                    st.warning("לא נמצאו תמונות.")
            else:
                st.error("שגיאה בחיבור לגוגל. וודא שהמפתחות נכונים.")
    else:
        st.info("בבקשה רשום שם מוצר.")
