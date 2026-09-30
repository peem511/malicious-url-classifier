# 🔗 Malicious URL Classifier — Mini Project: Machine Learning Application

จำแนก URL เป็น 4 ประเภท (`benign`, `defacement`, `phishing`, `malware`) จากข้อความของ URL ด้วย scikit-learn
และให้ใช้งานผ่าน Web App (Streamlit)

## โครงสร้างไฟล์
| ไฟล์ | รายละเอียด |
|---|---|
| `MaliciousURL_MiniProject.ipynb` | Notebook หลัก: Problem → Dataset → Preprocessing → เปรียบเทียบ 7 โมเดล → Evaluation → Discussion |
| `url_features.py` | ฟังก์ชันสร้าง lexical features 27 ตัว (ใช้ร่วมกันทั้ง Notebook และ Web App) |
| `app.py` | Web App 1 หน้า (Streamlit) |
| `models/url_classifier.joblib` | โมเดลสุดท้าย (Hybrid LinearSVC: TF-IDF + lexical features) |
| `models/model_info.json` | คะแนนของโมเดลบน Test |
| `data/malicious_phish.csv` | Dataset (ดาวน์โหลดจาก Kaggle — Notebook ดาวน์โหลดให้อัตโนมัติถ้าไม่มี) |

## ผลลัพธ์ (Test 128,203 URLs, แยก hostname จาก Train)
| โมเดล | Accuracy | Macro F1 |
|---|---|---|
| **Hybrid LinearSVC** | **0.9425** | **0.9154** |
| LinearSVC (TF-IDF) | 0.9421 | 0.9141 |
| Logistic Regression | 0.9066 | 0.8830 |
| Random Forest | 0.9113 | 0.8751 |
| KNN (k=5) | 0.8989 | 0.8508 |
| Decision Tree | 0.8529 | 0.7974 |
| Complement NB | 0.8535 | 0.7826 |
| Dummy (baseline) | 0.6678 | 0.2002 |

## วิธีรัน
```bash
pip install -r requirements.txt
streamlit run app.py
```
ฝึกโมเดลใหม่: เปิด `MaliciousURL_MiniProject.ipynb` ใน Jupyter หรือ Google Colab แล้ว Run all (~20–30 นาทีบน Colab)

## Dataset
Siddhartha, M. *Malicious URLs Dataset*. Kaggle. https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset
