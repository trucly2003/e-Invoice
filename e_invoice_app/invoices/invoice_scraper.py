from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import glob
import shutil
from invoices.models import InvoiceData

# 📁 Thư mục lưu hóa đơn tải về
DOWNLOAD_FOLDER = (
    r"D:\TaiLieuHocTap\khoaluantotnghiep\e-Invoice\e_invoice_app\invoices\downloads"
)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🚀 Cấu hình ChromeOptions để bỏ chặn tải file
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

# 📂 Cấu hình tải file không bị chặn
prefs = {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "safebrowsing.disable_download_protection": True,
    "profile.default_content_settings.popups": 0,
    "download.default_directory": DOWNLOAD_FOLDER,
}
chrome_options.add_experimental_option("prefs", prefs)


def fetch_latest_invoice():
    """Lấy hóa đơn mới nhất từ database và tải file XML & PDF"""
    latest_invoice = (
        InvoiceData.objects.exclude(invoice_lookup_link="")
        .exclude(invoice_code="")
        .latest("id")
    )

    if not latest_invoice:
        print("⚠ Không có hóa đơn nào để tra cứu.")
        return

    lookup_url = latest_invoice.invoice_lookup_link.strip()
    if not lookup_url.startswith("http"):
        lookup_url = "https://" + lookup_url

    invoice_code = latest_invoice.invoice_code
    print(f"🔍 Đang tra cứu hóa đơn {invoice_code} tại {lookup_url}")

    # 🚀 Khởi tạo trình duyệt Chrome
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # **1. Truy cập trang web**
        driver.get(lookup_url)
        driver.maximize_window()
        time.sleep(3)

        # **2. Nhập mã tra cứu**
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtInvoiceCode"]'))
        )
        search_box.clear()
        search_box.send_keys(invoice_code)

        # **3. Click vào nút tìm kiếm**
        search_button = driver.find_element(By.XPATH, '//*[@id="Button1"]')
        search_button.click()

        # **4. Chờ iframe xuất hiện và chuyển vào iframe**
        try:
            iframe_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "frameViewInvoice"))
            )
            driver.switch_to.frame(iframe_element)
        except:
            print("⚠ Không tìm thấy iframe, tiếp tục tìm kiếm trong trang chính.")

        # **5. Click vào nút Download để hiển thị menu**
        try:
            print("📥 Đang mở dropdown menu...")
            dropdown_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/form/div[3]/div[2]/div[3]/input")
                )
            )
            dropdown_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"❌ Lỗi khi click vào nút Download: {e}")
            return

        # **6. Lấy danh sách li và bấm vào từng mục**
        try:
            download_menu = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="divDownloads"]/ul'))
            )
            download_links = download_menu.find_elements(By.TAG_NAME, "li")

            if len(download_links) >= 6:
                # Bấm vào mục XML (li đầu tiên)
                print("📂 Đang tải file XML...")
                download_links[0].find_element(By.TAG_NAME, "a").click()
                time.sleep(2)
                downloaded_file = wait_for_download(invoice_code, "xml")
                if downloaded_file:
                    print(f"✅ File XML đã lưu đã tải")
                else:
                    print("⚠ Không tìm thấy file XML sau khi tải.")

                # Mở lại dropdown
                dropdown_button.click()
                time.sleep(2)

                # Bấm vào mục PDF (li thứ ba)
                print("📂 Đang tải file PDF...")
                download_links[4].find_element(By.TAG_NAME, "a").click()
                time.sleep(2)
                downloaded_file = wait_for_download(invoice_code, "pdf")
                if downloaded_file:
                    print(f"✅ File PDF đã lưu ")
                else:
                    print("⚠ Không tìm thấy file PDF sau khi tải.")
            else:
                print("⚠ Danh sách tải không đủ mục.")
        except Exception as e:
            print(f"❌ Lỗi khi tải file: {e}")

    except Exception as e:
        print(f"❌ Lỗi khi xử lý {lookup_url}: {e}")

    finally:
        driver.quit()


def wait_for_download(invoice_code, file_type, timeout=30):
    """Chờ file tải về thư mục downloads"""
    target_file_pattern = os.path.join(DOWNLOAD_FOLDER, f"*{invoice_code}*.{file_type}")

    start_time = time.time()
    while time.time() - start_time < timeout:
        matching_files = glob.glob(target_file_pattern)
        if matching_files:
            return matching_files[0]
        time.sleep(1)

    return None
