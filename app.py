import streamlit as st
import requests

# --- הגדרות שרת (Secrets) ---
# וודא שהגדרת את אלו ב-Advanced Settings ב-Streamlit Cloud
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    CX = st.secrets["GOOGLE_CX"]
except:
    st.error("שגיאה: מפתחות ה-API לא הוגדרו ב-Secrets.")
    st.stop()

# עיצוב דף האפליקציה
st.set_page_config(page_title="חיפוש מוצרי מכולת", page_icon="🛒", layout="centered")

# כותרות בעברית (יישור לימין)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    input { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_status_code=True)

st.title("🛒 מכולת - מוצא תמונות מוצרים")
st.write("הכנס את פרטי המוצר כדי למצוא תמונה רשמית לאתר שלך.")

# --- קלט מהמשתמש ---
product = st.text_input("שם המוצר (לדוגמה: קוטג' 5%):")
manufacturer = st.text_input("שם היצרן / חברה (אופציונלי):")
num_results = st.slider("כמה תמונות להציג?", 1, 5, 3)

if st.button("חפש תמונה"):
    if product:
        # בניית שאילתת חיפוש חכמה
        if manufacturer:
            query = f"{manufacturer} {product} תמונה רשמית מוצר"
        else:
            query = f"{product} תמונה רשמית מוצר"
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query,
            "searchType": "image",
            "num": num_results,
            "safe": "active",
            "lr": "lang_iw" # מגביל את החיפוש לתוצאות שקשורות לעברית
        }

        with st.spinner('מחפש תמונות בגוגל...'):
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])

                    if items:
                        st.success(f"מצאתי {len(items)} תמונות!")
                        for item in items:
                            st.subheader(item['title'])
                            # הצגת התמונה
                            st.image(item['link'], use_container_width=True)
                            st.write(f"[קישור למקור]({item['image']['contextLink']})")
                            st.divider()
                    else:
                        st.warning("לא נמצאו תמונות. נסה לשנות את שם המוצר.")
                else:
                    st.error(f"שגיאה מהשרת של גוגל: {response.status_code}")
            except Exception as e:
                st.error(f"קרתה שגיאה בחיבור: {e}")
    else:
        st.info("בבקשה הכנס לפחות את שם המוצר.")

# הערה משפטית בתחתית
st.caption("שים לב: יש לוודא זכויות יוצרים לפני שימוש מסחרי בתמונות.")
