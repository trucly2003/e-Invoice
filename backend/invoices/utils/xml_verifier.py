import os
import requests
import json
from datetime import datetime
from django.utils.timezone import make_aware
from invoices.models import ExtractedInvoice, SignatureVerification

folder_path = r"D:\TaiLieuHocTap\khoaluantotnghiep\e-Invoice\backend\invoices\xml_files"

def verify_signature_from_latest_xml(invoice):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xml')]
    if not files:
        return {"error": "Không tìm thấy file XML nào trong thư mục."}, 400

    newest_file = max(files, key=os.path.getmtime)

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi-VN,vi;q=0.9",
        "origin": "https://neac.gov.vn",
        "referer": "https://neac.gov.vn/vi/",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/135.0.0.0",
        "x-requested-with": "XMLHttpRequest",
    }

    url = "https://neac.gov.vn/vi/Home/VerifyFileByNeac"

    with open(newest_file, 'rb') as f:
        files = {
            "file": (os.path.basename(newest_file), f, "application/xml")
        }

        response = requests.post(url, files=files, headers=headers)

        if response.status_code == 200:
            try:
                result = response.json()
                signatures = result.get("signature", {}).get("data", [])
                saved_results = []

                for sig in signatures:
                    signer_name = sig.get("signer", {}).get("cn", "")
                    intact = sig.get("intact", "")
                    match_content = (intact == "Không bị thay đổi")
                    status = "PASS" if match_content else "FAIL"

                    SignatureVerification.objects.create(
                        invoice=invoice,
                        signer_name=signer_name,
                        status=status,
                        match_content=match_content,
                        result_detail=json.dumps(sig, ensure_ascii=False),
                        verified_at=make_aware(datetime.now())
                    )

                    saved_results.append({
                        "signer_name": signer_name,
                        "status": status,
                        "match_content": match_content
                    })

                return {"message": "Xác minh thành công", "results": saved_results}, 200

            except Exception as e:
                return {"error": f"Lỗi xử lý phản hồi: {str(e)}"}, 500
        else:
            return {"error": f"Lỗi gọi API: {response.status_code}"}, 500
