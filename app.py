import streamlit as st
import requests
from io import BytesIO

# --- הגדרות שרת (Secrets) ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    CX = st.secrets["GOOGLE_CX"]
except:
    st.error("שגיאה: מפתחות ה-API לא הוגדרו ב-Secrets ב-Streamlit Cloud.")
    st.stop()

# עיצוב דף האפליקציה
st.set_page_config(page_title="חיפוש תמונות למכולת", page_icon="🛒", layout="centered")

# עיצוב לעברית (RTL)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    div[data-baseweb="input"] { direction: rtl; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 מכולת - מוצא תמונות מוצרים")
st.write("חפש תמונות רשמיות של מוצרים בקלות:")

# --- קלט מהמשתמש ---
product = st.text_input("שם המוצר (חובה):", placeholder="לדוגמה: קוטג' 5%")
manufacturer = st.text_input("שם היצרן (אופציונלי):", placeholder="לדוגמה: תנובה")
num_results = st.slider("מספר תמונות להצגה", 1, 10, 3)

if st.button("חפש מוצר"):
    if product:
        # בניית שאילתה
        query = f"{manufacturer} {product} תמונה רשמית מוצר" if manufacturer else f"{product} תמונה רשמית מוצר"
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query,
            "searchType": "image",
            "num": num_results,
            "safe": "active",
            "lr": "lang_iw"
        }

        with st.spinner('מחפש...'):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                if items:
                    st.success(f"מצאתי {len(items)} תוצאות")
                    for item in items:
                        st.subheader(item['title'])
                        img_url = item['link']
                        
                        # הצגת התמונה
                        st.image(img_url, use_container_width=True)
                        
                        # יצירת כפתור הורדה
                        try:
                            img_response = requests.get(img_url, timeout=10)
                            if img_response.status_code == 200:
                                # הכנת הקובץ להורדה
                                img_bytes = BytesIO(img_response.content)
                                file_extension = img_url.split('.')[-1].split('?')[0]
                                if len(file_extension) > 4: file_extension = "jpg"
                                
                                st.download_button(
                                    label="📥 הורד תמונה זו",
                                    data=img_bytes,
                                    file_name=f"{product.replace(' ', '_')}.{file_extension}",
                                    mime=f"image/{file_extension}"
                                )
                        except:
                            st.write("לא ניתן ליצור כפתור הורדה ישיר לתמונה זו.")
                        
                        st.write(f"[קישור למקור התמונה]({item['image']['contextLink']})")
                        st.divider()
                else:
                    st.warning("לא נמצאו תמונות. נסה לחפש שוב במילים אחרות.")
            else:
                st.error(f"שגיאה: {response.status_code}. וודא שהמפתחות ב-Secrets נכונים.")
    else:
        st.info("בבקשה הכנס שם מוצר.")

st.caption("האפליקציה נועדה לשימוש פנימי במכולת. שים לב לזכויות יוצרים.")
