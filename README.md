# 🔗 Malicious URL Classifier — Mini Project: Machine Learning Application

จำแนก URL เป็น 4 ประเภท (`benign`, `defacement`, `phishing`, `malware`) จากข้อความของ URL ด้วย scikit-learn
และให้ใช้งานผ่าน Web App (Streamlit)

## โครงสร้างไฟล์
| ไฟล์ | รายละเอียด |
|---|---|
| `MaliciousURL_MiniProject.ipynb` | Notebook หลัก: Problem → Dataset → Preprocessing → เปรียบเทียบ 11 โมเดล (3 กลุ่ม Input) → Evaluation → Discussion |
| `url_features.py` | ฟังก์ชันสร้าง lexical features (27 ตัว → เลือกใช้ 22) (ใช้ร่วมกันทั้ง Notebook และ Web App) |
| `app.py` | Web App 1 หน้า (Streamlit) |
| `models/url_classifier.joblib` | โมเดลสุดท้าย (Hybrid LinearSVC: TF-IDF + lexical features) |
| `models/model_info.json` | คะแนนของโมเดลบน Test |
| `data/malicious_phish.csv` | Dataset (ดาวน์โหลดจาก Kaggle — Notebook ดาวน์โหลดให้อัตโนมัติถ้าไม่มี) |

## ผลลัพธ์
คัดเลือก 11 โมเดลใน 3 กลุ่ม Input บน Validation (แยก hostname) แล้วฝึกผู้ชนะแต่ละกลุ่มบน Train เต็ม และวัดบน Test 128,203 URLs

| ผู้ชนะกลุ่ม | Validation Macro F1 | Test Accuracy | Test Macro F1 |
|---|---|---|---|
| **Hybrid LinearSVC** (TF-IDF + Lexical) | **0.8913** | **0.9486** | **0.9192** |
| LinearSVC (TF-IDF) | 0.8888 | 0.9463 | 0.9171 |
| Random Forest (Lexical) | 0.8544 | 0.9073 | 0.8733 |
| Dummy (baseline) | – | 0.6678 | 0.2002 |

Features: TF-IDF char 3–5-grams เลือก 20,000 ตัวด้วย χ² + lexical features 22 ตัว (ตัด 5 ตัวที่ ANOVA F ต่ำสุด)

## วิธีรัน
```bash
pip install -r requirements.txt
streamlit run app.py
```
ฝึกโมเดลใหม่: เปิด `MaliciousURL_MiniProject.ipynb` ใน Jupyter หรือ Google Colab แล้ว Run all (~20–30 นาทีบน Colab)

## Dataset
Siddhartha, M. *Malicious URLs Dataset*. Kaggle. https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset
