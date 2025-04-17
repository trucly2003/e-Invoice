from lxml import etree
from signxml import XMLVerifier
import base64

def der_to_pem(cert_der: bytes) -> str:
    b64_cert = base64.b64encode(cert_der).decode("ascii")
    pem = "-----BEGIN CERTIFICATE-----\n"
    pem += "\n".join([b64_cert[i:i+64] for i in range(0, len(b64_cert), 64)])
    pem += "\n-----END CERTIFICATE-----"
    return pem

def verify_xml_signature(file_path=None, xml_bytes=None):
    try:
        if xml_bytes is None and file_path is None:
            return {
                "status": "FAIL",
                "message": "❌ Cần truyền file_path hoặc xml_bytes.",
                "signature_verified": False
            }

        if xml_bytes is None:
            with open(file_path, "rb") as f:
                xml_bytes = f.read()

        parser = etree.XMLParser(remove_blank_text=False)
        xml_tree = etree.fromstring(xml_bytes, parser=parser)

        ns = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}
        cert_el = xml_tree.find('.//ds:X509Certificate', namespaces=ns)
        if cert_el is None:
            return {
                "status": "FAIL",
                "message": "❌ Không tìm thấy X509Certificate trong XML",
                "signature_verified": False
            }

        cert_der = base64.b64decode(cert_el.text.strip())
        cert_pem = der_to_pem(cert_der)

        XMLVerifier().verify(
            xml_tree,
            x509_cert=cert_pem,
            require_x509=False,
            validate_schema=False
        )

        return {
            "status": "PASS",
            "message": "✅ Chữ ký hợp lệ (file gốc không chỉnh sửa)",
            "signature_verified": True
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "message": f"❌ Lỗi xác minh: {str(e)}",
            "signature_verified": False
        }
