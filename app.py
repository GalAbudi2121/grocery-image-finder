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

st.set_page_config(page_title="חיפוש מוצר ממוקד", page_icon="🛒")

# עיצוב לעברית (RTL)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    div[data-baseweb="input"] { direction: rtl; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 חיפוש מוצר ממוקד למכולת")
st.write("החיפוש מוגדר למצוא מוצרים ספציפיים בישראל.")

# --- קלט מהמשתמש ---
product = st.text_input("מה שם המוצר שאתה מחפש?", placeholder="לדוגמה: במבה אסם 80 גרם")
manufacturer = st.text_input("שם היצרן (לא חובה):")

if st.button("חפש מוצר"):
    if product:
        # בניית שאילתה חזקה בעברית עם סינון אתרים מחו"ל
        # השילוב של "מחיר" או "ברקוד" עוזר למצוא מוצרים אמיתיים ולא תמונות אווירה
        if manufacturer:
            query = f'"{manufacturer}" "{product}" מוצר'
        else:
            query = f'"{product}" מוצר תמונה'
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query,
            "searchType": "image",
            "num": 8,
            "safe": "active",
            "gl": "il",    # הגדרה לחיפוש מישראל
            "lr": "lang_iw" # הגדרה לתוצאות בעברית
        }

        with st.spinner('מחפש במאגרי המוצרים בישראל...'):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                if items:
                    st.success(f"מצאתי {len(items)} תוצאות רלוונטיות:")
                    # תצוגה של התמונות בגלריה (2 בשורה) כדי שיהיה קל להשוות
                    cols = st.columns(2)
                    for idx, item in enumerate(items):
                        with cols[idx % 2]:
                            img_url = item['link']
                            try:
                                img_response = requests.get(img_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                                if img_response.status_code == 200:
                                    st.image(img_response.content, use_container_width=True)
                                    st.caption(f"מקור: {item['displayLink']}")
                                    st.download_button(
                                        label="💾 שמור",
                                        data=img_response.content,
                                        file_name=f"{product}.jpg",
                                        mime="image/jpeg",
                                        key=f"btn_{idx}"
                                    )
                                    st.divider()
                            except:
                                continue
                else:
                    st.warning("לא נמצאו תמונות מדויקות. נסה לכתוב את השם קצת אחרת.")
            else:
                st.error("שגיאה בחיבור. ייתכן שנגמרה המכסה היומית של גוגל.")
    else:
        st.info("בבקשה הכנס שם מוצר.")
