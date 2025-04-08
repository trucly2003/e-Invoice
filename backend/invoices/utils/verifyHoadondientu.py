from invoices.models import ExtractedInvoice
import time
import requests
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_captcha_base64(driver):
    wait = WebDriverWait(driver, 10)
    img_element = wait.until(EC.presence_of_element_located((By.XPATH, '//img[contains(@src, "data:image/svg+xml;base64,")]')))
    src = img_element.get_attribute("src")
    return src.split("base64,")[1]


def solve_captcha_anticaptcha_svg(driver) -> str:
    try:
        base64_data = get_captcha_base64(driver)
        api_key = "88f56c7b7c9f3254f8e5bd057c07c855"
        url = "https://anticaptcha.top/api/captcha"
        payload = {
            "apikey": api_key,
            "img": "data:image/svg+xml;base64," + base64_data,
            "type": 28
        }
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        result = response.json()
        if result.get("success") and result.get("captcha"):
            return result["captcha"]
    except Exception as e:
        print("❌ Lỗi captcha:", e)
    return ""


def verify_invoice_by_id(invoice_id: int):
    try:
        invoice = ExtractedInvoice.objects.get(id=invoice_id)
    except ExtractedInvoice.DoesNotExist:
        return {"invoice_id": invoice_id, "status": "FAIL", "result_content": "Invoice not found"}

    tax_code = invoice.seller.tax_code
    serial = invoice.serial
    invoice_no = invoice.invoice_number
    vat = int(invoice.total_amount)
    grand = int(invoice.grand_total)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver.ChromeOptions())
    result_data = {"invoice_id": invoice_id, "status": "FAIL", "result_content": ""}

    try:
        driver.get("https://hoadondientu.gdt.gov.vn/")
        time.sleep(3)


        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "ant-modal-close"))).click()
        except:
            pass

        driver.find_element(By.ID, "nbmst").send_keys(tax_code)
        driver.find_element(By.XPATH, '//*[@id="lhdon"]/div/span').click()
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//ul[contains(@class, "ant-select-dropdown-menu")]/li[1]'))
        ).click()



        driver.find_element(By.XPATH, '//*[@id="khhdon"]').send_keys(serial)
        driver.find_element(By.XPATH, '//*[@id="shdon"]').send_keys(invoice_no)
        driver.find_element(By.XPATH, '//*[@id="tgtthue"]').send_keys(str(vat))
        driver.find_element(By.XPATH, '//*[@id="tgtttbso"]').send_keys(str(grand))

        captcha_text = solve_captcha_anticaptcha_svg(driver)
        if not captcha_text:
            result_data["result_content"] = "Không giải được captcha"
            return result_data

        driver.find_element(By.XPATH, '//*[@id="cvalue"]').send_keys(captcha_text)
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="__next"]/section/main/section/div/div/div/div/div[3]/div[1]/div[2]/div[1]/form/div[2]/div/button').click()
        time.sleep(3)

        result_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//section[contains(@class, "SearchContentBox")]'))
        )
        result_text = result_element.text.strip()
        result_data["result_content"] = result_text

        if "Tồn tại hóa đơn" in result_text and "Đã cấp mã hóa đơn" in result_text:
            result_data["status"] = "PASS"

    except Exception as e:
        result_data["result_content"] = f"Lỗi: {e}"
    finally:
        driver.quit()

    return result_data
