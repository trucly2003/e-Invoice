import os
import time
import glob
import datetime
import base64
import cloudinary.uploader
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from invoices.models import ExtractedInvoice, VerifiedXMLInvoice

def get_latest_xml_file(directory: str) -> str:
    xml_files = glob.glob(os.path.join(directory, "*.xml"))
    if not xml_files:
        raise FileNotFoundError("❌ Không tìm thấy file XML nào trong thư mục.")
    return max(xml_files, key=os.path.getmtime)

def get_text(root, xpath):
    el = root.find(xpath)
    return el.text.strip() if el is not None and el.text else ""

def parse_date(text):
    try:
        return datetime.datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except:
        return None

def crawl_save_and_verify_xml(extracted_invoice_id):
    download_dir = os.path.abspath("invoices/xml_files")
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=chrome_options)

    try:
        invoice = ExtractedInvoice.objects.get(id=extracted_invoice_id)
        ma_tra_cuu = invoice.ma_tra_cuu
        if not ma_tra_cuu:
            raise ValueError("❌ Không có mã tra cứu.")

        driver.get("https://van.ehoadon.vn/TCHD")
        driver.maximize_window()

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH,
                '/html/body/form/div[3]/div[2]/div/div[2]/div[2]/div[1]/div/table/tbody/tr[2]/td/div/div[1]/input[1]'))
        ).send_keys(ma_tra_cuu)

        driver.find_element(By.XPATH,
            '/html/body/form/div[3]/div[2]/div/div[2]/div[2]/div[1]/div/table/tbody/tr[2]/td/div/div[2]/span/input'
        ).click()

        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="frameViewInvoice"]'))
        )

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btnDownload"]'))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="LinkDownXML"]'))
        ).click()

        time.sleep(5)

        xml_path = get_latest_xml_file(download_dir)

        with open(xml_path, "rb") as f:
            raw_bytes = f.read()
            encoded_bytes = base64.b64encode(raw_bytes).decode("ascii")

        upload_result = cloudinary.uploader.upload(
            xml_path,
            resource_type="raw",
            folder="xml_files",
            public_id=ma_tra_cuu,
            use_filename=True,
            unique_filename=False
        )
        cloudinary_url = upload_result.get("secure_url")

        parser = etree.XMLParser(remove_blank_text=False)
        root = etree.fromstring(raw_bytes, parser=parser)

        VerifiedXMLInvoice.objects.update_or_create(
            invoice=invoice,
            defaults={
                "invoice_number": get_text(root, ".//SHDon"),
                "invoice_date": parse_date(get_text(root, ".//NLap")),
                "seller_tax_code": get_text(root, ".//NBan/MST"),
                "buyer_tax_code": get_text(root, ".//NMua/MST"),
                "total_amount": float(get_text(root, ".//TToan/TgTCThue") or 0),
                "vat_amount": float(get_text(root, ".//TToan/TgTThue") or 0),
                "grand_total": float(get_text(root, ".//TToan/TgTTTBSo") or 0),
                "cloudinary_url": cloudinary_url,
                "local_xml_path": xml_path,
                "raw_xml": encoded_bytes
            }
        )

    except Exception as e:
        print("❌ Lỗi crawl & verify XML:", e)

    finally:
        driver.quit()
