"""แปลงข้อความ URL เป็น lexical features 27 ตัว (ใช้ร่วมกันทั้ง Notebook และ Web App)

ฟังก์ชันในไฟล์นี้อ่านเฉพาะ "ข้อความ" ของ URL เท่านั้น ไม่มีการเปิดเว็บไซต์หรือค้น DNS
"""
from __future__ import annotations

import ipaddress
import math
import re
from collections import Counter
from urllib.parse import urlsplit

import numpy as np

SCHEME_PATTERN = r"^[A-Za-z][A-Za-z0-9+.-]*://"
CONTROL_PATTERN = r"[\x00-\x1F\x7F-\x9F]"

SUSPICIOUS_WORDS = (
    "login", "signin", "verify", "secure", "account", "update", "bank",
    "password", "confirm", "wallet", "paypal", "invoice", "webscr",
)
SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "cutt.ly", "tiny.cc",
}

FEATURE_NAMES = [
    "url_length", "host_length", "path_length", "query_length", "fragment_length",
    "subdomain_count", "path_depth", "query_param_count", "digit_count", "alpha_count",
    "special_count", "dot_count", "hyphen_count", "slash_count", "at_count", "percent_count",
    "equals_count", "underscore_count", "is_https", "host_is_ip", "has_port", "punycode",
    "non_ascii", "known_shortener", "suspicious_word", "entropy", "host_digit_count",
]


def url_entropy(value: str) -> float:
    """Shannon entropy ของตัวอักษรใน URL (URL ที่สุ่มตัวอักษรมักมีค่าสูง)"""
    if not value:
        return 0.0
    counts = Counter(value)
    n = len(value)
    return float(-sum((c / n) * math.log2(c / n) for c in counts.values()))


def extract_one_url(value: str) -> list[float]:
    """แปลง URL 1 รายการเป็นตัวเลข 27 ค่า ตามลำดับใน FEATURE_NAMES"""
    raw = str(value)
    # เติม http:// เฉพาะตอน parse เพื่อแยก host/path ได้ ข้อความต้นฉบับไม่ถูกแก้
    parse_value = raw if re.match(SCHEME_PATTERN, raw) else f"http://{raw}"
    try:
        parts = urlsplit(parse_value)
        host = (parts.hostname or "").lower()
        port = parts.port
    except ValueError:
        parts, host, port = urlsplit(""), "", None
    try:
        ipaddress.ip_address(host)
        host_is_ip = 1
    except ValueError:
        host_is_ip = 0
    host_parts = [p for p in host.split(".") if p]
    lower = raw.lower()
    return [
        len(raw), len(host), len(parts.path), len(parts.query), len(parts.fragment),
        max(0, len(host_parts) - 2),
        sum(bool(p) for p in parts.path.split("/")),
        len([p for p in parts.query.split("&") if p]),
        sum(c.isdigit() for c in raw), sum(c.isalpha() for c in raw),
        sum(not c.isalnum() for c in raw), raw.count("."), raw.count("-"),
        raw.count("/"), raw.count("@"), raw.count("%"), raw.count("="), raw.count("_"),
        int(parts.scheme.lower() == "https"), host_is_ip, int(port is not None),
        int("xn--" in host), int(any(ord(c) > 127 for c in raw)),
        int(host in SHORTENERS), int(any(w in lower for w in SUSPICIOUS_WORDS)),
        url_entropy(raw), sum(c.isdigit() for c in host),
    ]


def extract_lexical_features(values) -> np.ndarray:
    """แปลงรายการ URL เป็น matrix (n, 27) ใช้กับ sklearn FunctionTransformer"""
    return np.asarray(
        [extract_one_url(v) for v in np.asarray(values, dtype=object).ravel()],
        dtype=np.float32,
    )


def prepare_single_url(value: str) -> str:
    """ตรวจ input ของ Web App ด้วยกฎเดียวกับตอนทำความสะอาดข้อมูล"""
    if not isinstance(value, str):
        raise ValueError("กรุณากรอก URL เป็นข้อความ")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("กรุณากรอก URL ก่อนกด Predict")
    if re.search(CONTROL_PATTERN, cleaned):
        raise ValueError("URL มีอักขระควบคุม (control character) จึงไม่สามารถทำนายได้")
    return cleaned
