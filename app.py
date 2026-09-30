"""Malicious URL Classifier — Streamlit Web App (1 หน้า)

รัน: streamlit run app.py
แอปอ่านเฉพาะข้อความ URL ไม่มีการเปิดเว็บไซต์ที่ผู้ใช้กรอก
"""
import json
from pathlib import Path

import altair as alt
import joblib
import numpy as np
import pandas as pd
import streamlit as st

from url_features import FEATURE_NAMES, extract_lexical_features, prepare_single_url

BASE = Path(__file__).parent
MODEL_PATH = BASE / "models" / "url_classifier.joblib"
INFO_PATH = BASE / "models" / "model_info.json"

CLASS_INFO = {
    "benign": {
        "title": "Benign — URL ปกติ", "icon": "✅", "color": "#2E7D32", "bg": "#E8F5E9",
        "meaning": "รูปแบบของ URL นี้คล้ายกับ URL ทั่วไปที่ปลอดภัยในข้อมูลที่โมเดลเรียนรู้",
        "advice": "มีแนวโน้มปลอดภัย แต่ยังควรตรวจชื่อโดเมนให้ถูกต้องก่อนกรอกข้อมูลสำคัญ",
    },
    "defacement": {
        "title": "Defacement — เว็บไซต์ถูกเปลี่ยนเนื้อหา", "icon": "🛠️", "color": "#6A1B9A", "bg": "#F3E5F5",
        "meaning": "URL นี้คล้ายกับหน้าเว็บที่ถูกแฮ็กแล้วแก้ไขหรือแทรกเนื้อหาโดยไม่ได้รับอนุญาต",
        "advice": "ไม่ควรเชื่อเนื้อหาในหน้านั้น หากเป็นเว็บของหน่วยงานคุณ ให้แจ้งผู้ดูแลระบบตรวจสอบ",
    },
    "phishing": {
        "title": "Phishing — หลอกขโมยข้อมูล", "icon": "🎣", "color": "#E65100", "bg": "#FFF3E0",
        "meaning": "URL นี้คล้ายลิงก์ที่ปลอมตัวเป็นเว็บจริง เพื่อหลอกให้กรอกรหัสผ่าน ข้อมูลบัตร หรือข้อมูลบัญชี",
        "advice": "อย่ากรอกรหัสผ่านหรือข้อมูลส่วนตัว ให้เข้าเว็บไซต์ทางการโดยพิมพ์ที่อยู่เองแทนการกดลิงก์",
    },
    "malware": {
        "title": "Malware — แจกจ่ายโปรแกรมอันตราย", "icon": "☣️", "color": "#C62828", "bg": "#FFEBEE",
        "meaning": "URL นี้คล้ายลิงก์ที่ใช้ดาวน์โหลดหรือติดตั้งมัลแวร์ลงในเครื่องของผู้ใช้",
        "advice": "อย่าเปิดหรือดาวน์โหลดไฟล์จากลิงก์นี้ หากเผลอดาวน์โหลดแล้ว ให้สแกนเครื่องด้วยโปรแกรมป้องกันไวรัส",
    },
}
EXAMPLES = {
    "Wikipedia": "en.wikipedia.org/wiki/Machine_learning",
    "Phishing-like": "http://paypal.com.secure-login.verify-account.xyz/signin?id=123",
    "Malware-like": "http://192.168.10.5/files/setup.exe",
    "Defacement-like": "http://example.com/index.php?option=com_content&view=article&id=5",
}

st.set_page_config(page_title="Malicious URL Classifier", page_icon="🔗", layout="centered")


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_info():
    return json.loads(INFO_PATH.read_text(encoding="utf-8")) if INFO_PATH.exists() else {}


model = load_model()
info = load_info()

st.title("🔗 Malicious URL Classifier")
st.write("กรอก URL เพื่อให้โมเดล Machine Learning จำแนกว่าเป็น **benign, defacement, phishing หรือ malware**  \n"
         "ระบบวิเคราะห์จาก **ข้อความของ URL เท่านั้น** และไม่เปิดเว็บไซต์ที่กรอก")

if "url" not in st.session_state:
    st.session_state.url = ""

st.caption("ลองตัวอย่าง:")
cols = st.columns(len(EXAMPLES))
for col, (label, value) in zip(cols, EXAMPLES.items()):
    if col.button(label, use_container_width=True):
        st.session_state.url = value

url = st.text_input("URL", key="url", placeholder="เช่น http://example.com/login")
predict = st.button("🔍 Predict", type="primary", use_container_width=True)

if predict:
    try:
        text = prepare_single_url(url)
    except ValueError as error:
        st.error(str(error))
    else:
        X = np.array([text], dtype=object)
        label = str(model.predict(X)[0])
        c = CLASS_INFO[label]
        st.markdown(
            f"""<div style="border-left:8px solid {c['color']};background:{c['bg']};padding:18px 20px;
            border-radius:10px;margin:12px 0;color:#1a1a1a">
            <div style="font-size:0.9rem;opacity:.75">ผลการทำนาย</div>
            <div style="font-size:1.7rem;font-weight:700;color:{c['color']}">{c['icon']} {c['title']}</div>
            <div style="margin-top:10px"><b>ความหมาย:</b> {c['meaning']}</div>
            <div style="margin-top:6px"><b>คำแนะนำ:</b> {c['advice']}</div></div>""",
            unsafe_allow_html=True,
        )

        classes = list(model.classes_)
        if hasattr(model, "decision_function"):
            scores = model.decision_function(X)[0]
            score_title = "คะแนนตัดสินใจของแต่ละคลาส (decision score — คลาสที่สูงสุดคือคำตอบ, ไม่ใช่ความน่าจะเป็น)"
        else:
            scores = model.predict_proba(X)[0]
            score_title = "ความน่าจะเป็นของแต่ละคลาส"
        st.write(f"**{score_title}**")
        chart_df = pd.DataFrame({"class": classes, "score": scores,
                                 "color": [CLASS_INFO[k]["color"] if k == label else "#B0B7C3" for k in classes]})
        bars = alt.Chart(chart_df).mark_bar(cornerRadius=3).encode(
            x=alt.X("score:Q", title="score"),
            y=alt.Y("class:N", sort=list(CLASS_INFO), title=None),
            color=alt.Color("color:N", scale=None),
            tooltip=["class", alt.Tooltip("score:Q", format=".3f")],
        )
        zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#666").encode(x="x:Q")
        st.altair_chart((bars + zero).properties(height=180), use_container_width=True)

        with st.expander("ดู lexical features ที่โมเดลใช้กับ URL นี้"):
            feats = pd.Series(extract_lexical_features(X)[0], index=FEATURE_NAMES, name="value")
            st.dataframe(feats.to_frame(), use_container_width=True)

st.divider()
with st.expander("ℹ️ เกี่ยวกับโมเดล"):
    if info:
        s = info.get("test_scores", {})
        m1, m2, m3 = st.columns(3)
        m1.metric("Accuracy (Test)", f"{s.get('accuracy', 0):.2%}")
        m2.metric("Macro F1 (Test)", f"{s.get('f1_macro', 0):.4f}")
        m3.metric("Macro Recall (Test)", f"{s.get('recall_macro', 0):.4f}")
        st.write(f"โมเดล: **{info.get('model')}** (TF-IDF char 3–5-grams + lexical features 27 ตัว), "
                 f"ฝึกด้วย {info.get('train_rows', 0):,} URLs และทดสอบกับ {info.get('test_rows', 0):,} URLs ที่แยก hostname จากชุดฝึก")
    st.write("Dataset: Malicious URLs Dataset (Kaggle, sid321axn)")
    st.warning("ข้อจำกัด: ใน Dataset นี้ URL ปกติส่วนใหญ่เขียนแบบไม่มี `http(s)://www.` และมี path ยาว "
               "โมเดลจึงอาจทาย URL ปกติที่เป็นหน้าแรกสั้น ๆ หรือขึ้นต้นด้วย `https://www.` ว่าเป็น phishing (dataset bias)")
    st.caption("ผลลัพธ์เป็นการคาดการณ์จากรูปแบบข้อความเท่านั้น ใช้ประกอบการตัดสินใจ ไม่ใช่การรับรองความปลอดภัย")
