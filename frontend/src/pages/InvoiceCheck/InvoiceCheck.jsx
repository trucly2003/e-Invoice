import axios from "axios"
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { TfiMoney } from "react-icons/tfi";
import { CiShoppingCart } from "react-icons/ci";
import { AiTwotoneBank } from "react-icons/ai";
import { TbInvoice } from "react-icons/tb";
import './InvoiceCheck.css'
import CheckResult from "../../components/CheckResult/CheckResult";
export default function InvoiceCheck()  {
    const {id} = useParams()
    const [invoiceInfo, setInvoiceInfo] = useState(null)
    const moneyFormatter = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 9});
    const [companiesCheck, setCompaniesCheckCheck] = useState([])
    const [taxDeparmentCheck, setTaxDepartmentCheck] = useState(null)
    const [eSignCheck, setESignCheck] = useState(null)
    const fetchInvoiceInfo = async () => {
        const url = 'http://localhost:8000/api/upload-invoice/' + id + "/"
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(url, {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            })
            setInvoiceInfo(response['data'])
        }
        catch (e) {
            console.log(e)
        }
    }
    const fetchVerifyCompanies = async () => {
        const url = 'http://localhost:8000/api/invoices/' + id + '/verify-companies/'
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(url, {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            })
            const data = response['data']
            const verifyResult =  Object.keys(data).map(key => {
                let postFix = "người mua"
                if (key === 'seller') {
                    postFix = "người bán"
                }
                return {
                    headingMessage: (data[key]['status'] === "PASS" ? 'Đúng thông tin ' : "Sai thông tin ") + postFix,
                    details: data[key]['message'].split(';'),
                    success: data[key]['status'] === "PASS"
                }
            })
            setCompaniesCheckCheck(verifyResult)
           
        }
        catch (e) {
            console.log(e)
        }
    }
    const fetchTaxDepartment = async () => {
        const url = 'http://localhost:8000/api/invoices/' + id + '/verify/'
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(url, {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            })
            const data = response['data']
            const verifyResult =  {
                headingMessage: 'Kiểm tra trên hệ thống của cục thuế',
                details: data['result_content'].split('\n'),
                success: data['status'] === "PASS"
            }
            
            setTaxDepartmentCheck(verifyResult)
        }
        catch (e) {
            console.log(e)
        }
    }

	const fetchSignature = async () => {
		const url = 'http://localhost:8000/api/verify-xml/' + id + '/verify-signature/'
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(url, {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            })
            const data = response['data']
            const verifyResult =  {
                headingMessage: data['message'],
                details: data['results'].map(sign => {
					if (sign['match_content']) {
						return "Được ký bởi " + sign['signer_name']
					}
					return "Chữ ký của " + sign['signer_name'] + " không chính xác"
				}),
                success: data['overall_status']
            }
            
            setESignCheck(verifyResult)
        }
        catch (e) {
            console.log(e)
        }
	}

    useEffect(() => {
        fetchInvoiceInfo()
		fetchSignature()
        fetchTaxDepartment()
        fetchVerifyCompanies()
    }, [])
    return (<div className="container-fluid">
        <div className="row">
            <div className="col-md-6">
                {invoiceInfo && <object className='file-view' data={invoiceInfo['file']} type="application/pdf"></object>}
            </div>
            <div className="col-md-6">
                {invoiceInfo && (<>
                    <ul className=" list-group list-group-flush" >
                    <li className="list-group-item">
                        <h6 className="list-header p-1"><AiTwotoneBank size={20} className="pe-1" />ĐƠN VỊ BÁN HÀNG</h6>
                        <ul className="list-unstyled">
                            <li className="d-flex"><span className="detail-field-lable">Đơn vị:</span> <span className="text-uppercase fw-bolder">{invoiceInfo['extracted'][0]['seller']['name']}</span> </li>
                            <li className="d-flex"><span className="detail-field-lable">Mã số thuế:</span> <span className="text-uppercase fw-bolder">{invoiceInfo['extracted'][0]['seller']['tax_code']}</span></li>
                            <li className="d-flex"><span className="detail-field-lable">Địa chỉ:</span> <span className="text-uppercase fw-bolder">{invoiceInfo['extracted'][0]['seller']['address']}</span></li>
                        </ul>
                    </li>
                    <li className="list-group-item">
                        <h6 className="list-header p-1"><CiShoppingCart size={20} className="pe-1" />ĐƠN VỊ MUA HÀNG</h6>
                        <ul className="list-unstyled ">
                            <li className="d-flex"><span className="detail-field-lable">Đơn vị:</span> <span className="text-uppercase fw-bolder">{invoiceInfo['extracted'][0]['buyer']['name']}</span> </li>
                            <li className="d-flex"><span className="detail-field-lable">Mã số thuế:</span> <span className="text-uppercase fw-bolder">{invoiceInfo['extracted'][0]['buyer']['tax_code']}</span></li>
                            <li className="d-flex"><span className="detail-field-lable">Địa chỉ:</span> <span className="text-uppercase fw-bolder">{invoiceInfo['extracted'][0]['buyer']['address']}</span></li>
                        </ul>
                    </li>
                    <li className="list-group-item">
                        <h6 className="list-header p-1"><TfiMoney size={20} className="pe-1" />THÔNG TIN THANH TOÁN</h6>
                        <ul className="list-unstyled ">
                            <li className="d-flex"><span className="detail-field-lable1">Tổng tiền hàng:</span> <span className="text-uppercase fw-bolder">{moneyFormatter.format(invoiceInfo['extracted'][0]['total_amount'])}</span> </li>
                            <li className="d-flex"><span className="detail-field-lable1">Tổng GTGT thuế (10%):</span> <span className="text-uppercase fw-bolder">{moneyFormatter.format(invoiceInfo['extracted'][0]['vat_amount'])}</span></li>
                            <li className="d-flex"><span className="detail-field-lable1">Tổng tiền thanh toán:</span> <span className="text-uppercase fw-bolder">{moneyFormatter.format(invoiceInfo['extracted'][0]['grand_total'])}</span></li>
                        </ul>

                    </li>
                    <li className="list-group-item"> 
                        <h6 className="list-header p-1"><TbInvoice size={20} className="pe-1" />THÔNG TIN HÓA ĐƠN</h6>
                        <ul className="list-unstyled ">
                            <li className="d-flex"><span className="detail-field-lable1">Mã hóa đơn:</span> <span className="text-uppercase fw-bolder">{invoiceInfo['extracted'][0]['invoice_number']}</span> </li>
                            
                            <li className="d-flex"><span className="detail-field-lable1">Ngày hóa đơn:</span> <span className="text-uppercase fw-bolder">{new Date(invoiceInfo['extracted'][0]['invoice_date']).toLocaleDateString('vi-VN')}</span></li>
                            <li className="d-flex"><span className="detail-field-lable1">Ngày tải lên</span> <span className="text-uppercase fw-bolder">{new Date(invoiceInfo['uploaded_at']).toLocaleDateString('vi-VN')}</span></li>
                        </ul>

                    </li>
                </ul>
                <div className="mt-5 p-4 border">
                    <div className="row">
                        <div className="col-md-6">
                        <h6 className="text-uppercase fw-bolder text-decoration-underline">Kết quả kiểm tra hóa đơn</h6>
                        {
                            companiesCheck.map((result, index) => <CheckResult key={index} {...result} /> )
                        }
						{
							eSignCheck && <CheckResult {...eSignCheck} />
						} 
                        </div>
                        <div className="col-md-6">
                        <h6 className="text-uppercase fw-bolder text-decoration-underline">Kết quả kiểm tra với hệ thống cục thuế</h6>   
                        {taxDeparmentCheck && <CheckResult {...taxDeparmentCheck} />}
                        </div>
                    </div>
                </div>    
            </>)}
                
            </div>
        </div>
    </div>)
}