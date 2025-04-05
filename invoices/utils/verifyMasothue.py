from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.utils import timezone
from invoices.models import CompanyVerification, Company
import time

def crawl_taxcode_data(tax_code):
    url = "https://masothue.com/"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Chạy ẩn
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

        # ✅ Lấy tên công ty
        name = driver.find_element(
            By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[2]/td[2]/span'
        ).text.strip()

        # ✅ Lấy địa chỉ
        try:
            address = driver.find_element(
                By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[4]/td[2]/span'
            ).text.strip()
        except:
            address = ""

        # ✅ Lấy trạng thái
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

    if company.name.strip() == crawled_data.get("name", "").strip():
        msg.append("Tên trùng khớp")
    else:
        msg.append("Tên KHÔNG khớp")

    if company.address.strip() == crawled_data.get("address", "").strip():
        msg.append("Địa chỉ trùng khớp")
    else:
        msg.append("Địa chỉ KHÔNG khớp")

    verify_status = "PASS" if "KHÔNG" not in " ".join(msg) else "FAIL"
    return verify_status, "; ".join(msg)