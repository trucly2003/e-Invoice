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
    # options.add_argument("--headless")  # Nếu cần chạy nền
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(3)
        driver.maximize_window()

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="search"]'))
        )
        search_box.clear()
        search_box.send_keys(tax_code)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"🔍 Đã nhập MST: {tax_code}, đang tìm kiếm...")

        time.sleep(5)

        # ✅ Lấy tên công ty
        name = driver.find_element(By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[2]/td[2]/span').text.strip()

        # ✅ Lấy địa chỉ công ty
        try:
            address_element = driver.find_element(By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[4]/td[2]/span')
            address = address_element.text.strip()
        except:
            address = "Không tìm thấy địa chỉ"

        # ✅ Lấy trạng thái hoạt động
        try:
            status_element = driver.find_element(By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[10]/td[2]/a')
            status = status_element.text.strip()
        except:
            status = "Không rõ trạng thái"

        # ✅ Cập nhật vào database
        company, created = Company.objects.update_or_create(
            tax_code=tax_code,
            defaults={
                "name": name,
                "address": address,
                "status": status,
                "last_crawled": timezone.now()
            }
        )

        print(f"✅ Lấy dữ liệu thành công: {name} ({tax_code}) - {address}")
        return company

    except Exception as e:
        print(f"❌ Lỗi khi crawl MST {tax_code}: {e}")
        return None

    finally:
        driver.quit()


def verify_company_data(company, crawled_obj):
    if not crawled_obj:
        status = "FAIL"
        message = "Không crawl được dữ liệu"
    else:
        msg = []
        if company.name.strip() == crawled_obj.name.strip():
            msg.append("Tên trùng khớp")
        else:
            msg.append("Tên KHÔNG khớp")

        if company.address.strip() == crawled_obj.address.strip():
            msg.append("Địa chỉ trùng khớp")
        else:
            msg.append("Địa chỉ KHÔNG khớp")

        status = "PASS" if "KHÔNG" not in " ".join(msg) else "FAIL"
        message = "; ".join(msg)

    verification = CompanyVerification.objects.create(
        company=company,
        source="masothue",
        status=status,
        message=message
    )
    return verification
