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
st.set_page_config(page_title="חיפוש תמונות נקיות למכולת", page_icon="🛒", layout="centered")

# עיצוב לעברית (RTL) ושיפור כפתורים
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    div[data-baseweb="input"] { direction: rtl; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    button { background-color: #2e7d32 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 חיפוש תמונות מוצר נקיות")
st.write("האפליקציה תנסה למצוא תמונות רשמיות על רקע לבן ללא הסחות דעת.")

# --- קלט מהמשתמש ---
product = st.text_input("שם המוצר:", placeholder="לדוגמה: במבה אסם 80 גרם")
manufacturer = st.text_input("שם היצרן (אופציונלי):", placeholder="לדוגמה: אסם")

if st.button("מצא תמונה נקייה"):
    if product:
        # בניית שאילתה חכמה עם סינון אתרים (Negative keywords)
        # אנחנו מוסיפים "-site:amazon.com" וכו' כדי לסנן אותם
        exclude_sites = "-site:amazon.* -site:youtube.com -site:pinterest.* -site:shutterstock.com -site:zap.co.il"
        
        # הוספת מילות מפתח לתמונה נקייה
        clean_keywords = "צילום מוצר רקע לבן product white background"
        
        if manufacturer:
            query = f"{manufacturer} {product} {clean_keywords} {exclude_sites}"
        else:
            query = f"{product} {clean_keywords} {exclude_sites}"
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query,
            "searchType": "image",
            "num": 6, # מביא קצת יותר תוצאות כדי שתוכל לבחור את הכי נקייה
            "safe": "active",
            "imgSize": "large", # מעדיף תמונות גדולות ואיכותיות
            "imgType": "photo" # נמנע מאיורים/וקטורים
        }

        with st.spinner('מסנן תמונות ומחפש את הכי מתאימות...'):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                if items:
                    st.success(f"מצאתי {len(items)} אפשרויות נקיות:")
                    for item in items:
                        # הצגת כותרת האתר כדי שתדע מאיפה זה הגיע (למשל אתר היצרן)
                        st.info(f"מקור: {item['displayLink']}")
                        img_url = item['link']
                        
                        st.image(img_url, use_container_width=True)
                        
                        # כפתור הורדה
                        try:
                            img_response = requests.get(img_url, timeout=10)
                            if img_response.status_code == 200:
                                img_bytes = BytesIO(img_response.content)
                                file_name = f"{product.replace(' ', '_')}.jpg"
                                
                                st.download_button(
                                    label="💾 שמור תמונה זו למכשיר",
                                    data=img_bytes,
                                    file_name=file_name,
                                    mime="image/jpeg",
                                    key=img_url # מפתח ייחודי לכל כפתור
                                )
                        except:
                            st.write("לא ניתן להוריד אוטומטית - לחץ לחיצה ארוכה על התמונה לשמירה.")
                        
                        st.divider()
                else:
                    st.warning("לא נמצאו תמונות מספיק טובות. נסה להוריד את שם היצרן או לקצר את השם.")
            else:
                st.error("שגיאה בחיבור לגוגל. וודא שחבילת החיפוש החינמית לא נגמרה (100 ליום).")
    else:
        st.info("בבקשה רשום שם מוצר.")

st.caption("הטיפ של Gemini: ככל שתהיה ספציפי יותר (למשל 'במבה 80 גרם' במקום רק 'במבה'), התמונה תהיה מדויקת יותר.")
