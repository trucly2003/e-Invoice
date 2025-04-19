from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from invoices.models import CompanyVerification, Company
from rapidfuzz import fuzz
import unicodedata
import re
import time


def normalize_text(text):
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = text.lower()

    # Thay thế từ viết tắt phổ biến
    replacements = {
        "kcn": "khu cong nghiep",
        "tp": "thanh pho",
        "tp.": "thanh pho",
        "tp ho chi minh": "thanh pho ho chi minh",
        "hcmc": "thanh pho ho chi minh",
        "vn": "viet nam"
    }
    for k, v in replacements.items():
        text = re.sub(rf"\b{k}\b", v, text)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_company_name(name):
    """Loại các cụm không cần thiết, normalize đơn giản"""
    name = name.lower()
    name = unicodedata.normalize("NFD", name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')  # Bỏ dấu
    name = re.sub(r"[^a-z0-9\s\-]", " ", name)  # Bỏ ký tự đặc biệt như ()
    name = re.sub(r"\b(cong|ty|co|phan|tnhh|mtv|trach|nhiem|huu|han|limited|ltd|international)\b", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

def is_similar(a, b):
    a_clean = clean_company_name(a)
    b_clean = clean_company_name(b)
    score = fuzz.token_set_ratio(a_clean, b_clean)
    return score >= 80 or a_clean in b_clean or b_clean in a_clean



def is_active_status(status_text):
    """Xác định trạng thái hoạt động từ text OCR có thể sai"""
    status_text = normalize_text(status_text)
    active_keywords = [
        "hoat dong",
        "dang hoat dong",
        "ang hoat ong",
        "cap gcn",
        "chua ngung"
    ]
    return any(kw in status_text for kw in active_keywords)


def crawl_taxcode_data(tax_code):
    url = "https://masothue.com/"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 ...")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(2)

        driver.maximize_window()
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="search"]'))
        )
        search_box.clear()
        search_box.send_keys(tax_code)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        name = driver.find_element(
            By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[2]/td[2]/span'
        ).text.strip()

        try:
            address = driver.find_element(
                By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[4]/td[2]/span'
            ).text.strip()
        except:
            address = ""

        try:
            status_text = driver.find_element(
                By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[10]/td[2]/a'
            ).text.strip()
        except:
            status_text = ""

        return {
            "name": name,
            "address": address,
            "status": status_text,
        }

    except Exception as e:
        print(f"❌ Lỗi crawl MST: {e}")
        return None

    finally:
        driver.quit()


def verify_company_data(company, crawled_data):
    if not crawled_data:
        return "FAIL", "Không crawl được dữ liệu"

    msg = []

    company_name = normalize_text(company.name)
    crawled_name = normalize_text(crawled_data.get("name", ""))

    cleaned_company_name = clean_company_name(company_name)
    cleaned_crawled_name = clean_company_name(crawled_name)

    if is_similar(cleaned_company_name, cleaned_crawled_name):
        msg.append("Tên trùng khớp")
    else:
        msg.append("Tên KHÔNG khớp")

    company_address = normalize_text(company.address)
    crawled_address = normalize_text(crawled_data.get("address", ""))

    if is_similar(company_address, crawled_address):
        msg.append("Địa chỉ trùng khớp")
    else:
        msg.append("Địa chỉ KHÔNG khớp")

    crawled_status = crawled_data.get("status", "")
    if is_active_status(crawled_status):
        msg.append("Trạng thái đang hoạt động")
    else:
        msg.append("Trạng thái KHÔNG hoạt động")

    # Debug log
    print("📌 Company name:", company_name)
    print("📌 Crawled name:", crawled_name)
    print("📌 Company addr:", company_address)
    print("📌 Crawled addr:", crawled_address)
    print("📌 Status:", crawled_status)

    verify_status = "PASS" if all("KHÔNG" not in m for m in msg) else "FAIL"
    return verify_status, "; ".join(msg)
