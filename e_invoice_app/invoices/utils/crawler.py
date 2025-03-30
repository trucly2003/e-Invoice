# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from django.utils import timezone
# from invoices.models import CrawledCompanyData, Invoice
# import time
#
# def crawl_taxcode_data(tax_code):
#     """Dùng Selenium để crawl dữ liệu công ty từ masothue.com dựa trên mã số thuế."""
#     url = "https://masothue.com/"
#
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")  # Chống detect bot
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
#
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#
#     try:
#         driver.get(url)
#         time.sleep(3)  # Đợi trang load lâu hơn để tránh bị chặn
#         driver.maximize_window()
#
#         search_box = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, '//*[@id="search"]'))
#         )
#         search_box.clear()  # Xóa nội dung cũ nếu có
#         search_box.send_keys(tax_code)  # Nhập mã số thuế
#
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#
#         print(f"🔍 Đã nhập MST: {tax_code}, đang tìm kiếm...")
#         time.sleep(5)  # Chờ kết quả hiển thị
#
#         # ✅ Lấy tên công ty
#         name = driver.find_element(By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[2]/td[2]/span').text.strip()
#
#         # ✅ Lấy địa chỉ công ty
#         try:
#             address_element = driver.find_element(By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[4]/td[2]/span')
#             address = address_element.text.strip()
#         except:
#             address = "Không tìm thấy địa chỉ"
#
#         # ✅ Lấy trạng thái hoạt động
#         try:
#             status_element = driver.find_element(By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody/tr[10]/td[2]/a')
#             status = status_element.text.strip()
#         except:
#             status = "Không rõ trạng thái"
#
#         # ✅ Lưu vào database hoặc cập nhật nếu đã có
#         company, created = CrawledCompanyData.objects.update_or_create(
#             tax_code=tax_code,
#             defaults={
#                 "name": name,
#                 "address": address,
#                 "status": status,
#                 "last_crawled": timezone.now()
#             }
#         )
#
#         print(f"✅ Lấy dữ liệu thành công: {name} ({tax_code}) - {address}")
#         return company
#
#     except Exception as e:
#         print(f"❌ Lỗi khi crawl MST {tax_code}: {e}")
#         return None
#
#     finally:
#         driver.quit()  # Đóng trình duyệt
#
#
# def crawl_seller_buyer(invoice_id):
#     """Crawl dữ liệu cho cả người bán & người mua của một hóa đơn."""
#     try:
#         invoice = Invoice.objects.get(id=invoice_id)
#
#         # 🔍 Kiểm tra người bán (Seller)
#         if not invoice.crawled_seller:
#             print(f"🔍 Crawl dữ liệu cho người bán MST: {invoice.seller.tax_code}")
#             invoice.crawled_seller = crawl_taxcode_data(invoice.seller.tax_code)
#
#         # 🔍 Kiểm tra người mua (Buyer)
#         if not invoice.crawled_buyer:
#             print(f"🔍 Crawl dữ liệu cho người mua MST: {invoice.buyer.tax_code}")
#             invoice.crawled_buyer = crawl_taxcode_data(invoice.buyer.tax_code)
#
#         invoice.save()
#         print(f"✅ Crawl hoàn thành cho hóa đơn {invoice.serial}")
#
#     except Invoice.DoesNotExist:
#         print(f"❌ Không tìm thấy hóa đơn ID {invoice_id}")
