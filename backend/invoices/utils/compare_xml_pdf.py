import base64
from decimal import Decimal
from invoices.utils.xml_verifier import verify_xml_signature

def compare_and_verify_xml(invoice):
    try:
        verified = invoice.verifiedxmlinvoice
    except Exception:
        return {
            "status": "FAIL",
            "message": "❌ Chưa có dữ liệu XML để so sánh.",
            "signature_verified": False
        }

    mismatches = []

    def check(field_name, pdf_value, xml_value):
        try:
            if isinstance(pdf_value, (int, float, Decimal)) and isinstance(xml_value, (int, float, Decimal)):
                if Decimal(str(pdf_value)) != Decimal(str(xml_value)):
                    mismatches.append(f"❌ {field_name}: PDF={pdf_value} <> XML={xml_value}")
            else:
                if str(pdf_value).strip() != str(xml_value).strip():
                    mismatches.append(f"❌ {field_name}: PDF={pdf_value} <> XML={xml_value}")
        except Exception as e:
            mismatches.append(f"⚠️ Lỗi khi so sánh {field_name}: {e}")

    check("Số hóa đơn", invoice.invoice_number, verified.invoice_number)
    check("Ngày hóa đơn", invoice.invoice_date, verified.invoice_date)
    check("MST người bán", invoice.seller.tax_code if invoice.seller else None, verified.seller_tax_code)
    check("MST người mua", invoice.buyer.tax_code if invoice.buyer else None, verified.buyer_tax_code)
    check("Tổng tiền", invoice.total_amount, verified.total_amount)
    check("VAT", invoice.vat_amount, verified.vat_amount)
    check("Tổng thanh toán", invoice.grand_total, verified.grand_total)

    if mismatches:
        return {
            "status": "FAIL",
            "message": "❌ Dữ liệu PDF và XML KHÔNG khớp.",
            "signature_verified": False,
            "errors": mismatches
        }

    try:
        # ✅ DECODE base64 đúng cách để lấy lại bytes gốc
        raw_bytes = base64.b64decode(verified.raw_xml.encode("ascii"))
    except Exception as e:
        return {
            "status": "FAIL",
            "message": f"❌ Lỗi giải mã raw_xml: {e}",
            "signature_verified": False
        }

    # ✅ Gọi xác minh chữ ký đúng cách
    sig_result = verify_xml_signature(file_path=verified.local_xml_path)


    if sig_result["status"] == "PASS":
        return {
            "status": "PASS",
            "message": "✅ Dữ liệu khớp và chữ ký số hợp lệ.",
            "signature_verified": True
        }
    else:
        return {
            "status": "FAIL",
            "message": "⚠️ Dữ liệu khớp nhưng chữ ký không hợp lệ.",
            "signature_verified": False,
            "signature_error": sig_result["message"]
        }
