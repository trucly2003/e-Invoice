import { useContext, useEffect, useState } from 'react'
import { UserContext } from '../../configs/context'
import axios from 'axios'
import { BsFillXCircleFill } from "react-icons/bs";
import { FaCircleCheck } from "react-icons/fa6";
export default function History() {
    const [invoices, setInvoices] = useState([])
    const [pageTotal, setPageTotal] = useState(0)
    const [page, setPage] = useState(1)
    const [kw, setKw] = useState('')
    const {user} = useContext(UserContext)
    const fetchInvoices = async () => {
        const url = `http://localhost:8000/api/user/${user['id']}/get_check_result/?page=${page}&kw=${kw}`
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(url, {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            })
            setInvoices(response['data']['results'])
			setPageTotal(Math.floor(response['data']['count'] / 10) + 1)
        } catch (e) {
            console.log(e)}
        }
    useEffect(() => {
        fetchInvoices()
    },[page, kw])

    const renderPaginateNav = () => {
        const visiblePageCount = 5
        let from  = Math.max(1, page - Math.floor(visiblePageCount / 2))
        let to = Math.min(pageTotal, from + visiblePageCount - 1);
        if (to - from + 1 < visiblePageCount) {
            from = Math.max(1, to - visiblePageCount + 1);
        }
        return Array.from(
            { length: to - from + 1 },
            (_, i) => from + i
          ).map(value => <li key={value} className="page-item"><button onClick={e => setPage(e.target.value)} className={["page-link", value === page ? "active" : ''].join(' ')}>{value}</button></li>)
    }

    return (
    <div className="section-background">
        <div className='container'>
            <div className='row'>
            <div className='col-md-10'><div><h5>Check History</h5></div></div>
            <div className='col-md-2'>
                <div className="input-group">
                        <input value={kw} onChange={(e) => setKw(e.target.value)} className="form-control form-control-md" type="search" placeholder="Quick search" aria-label="Search"/>
                        <button className="btn btn-primary px-4" type="submit">
                                <i className="bi bi-search"></i>
                            </button>
                    </div>
            </div>
            </div>
        </div>
        <div className='mt-5'>
            <table className='table'>
                <thead>
                    <tr>
                        <th><div className='d-flex justify-content-center'>#</div></th>
                        <th><div className='d-flex justify-content-center'>File Name</div></th>
                        <th><div className='d-flex justify-content-center'>Invoice Code</div></th>
                        <th><div className='d-flex justify-content-center'>Seller</div></th>
                        <th><div className='d-flex justify-content-center'>Buyer</div></th>
                        <th><div className='d-flex justify-content-center'>Check Date</div></th>
                        <th><div className='d-flex justify-content-center'>Check</div></th>
                    </tr>
                </thead>
                <tbody>
                    {
                        invoices.map((invoice, index) => {
                            return <tr key={index}>
                                <td><div className='d-flex justify-content-center'>{invoice['id']}</div></td>
                                <td><div className='d-flex justify-content-center'>{invoice['name'].replace(/^.*[\\/]/, '')}</div></td>
                                <td><div className='d-flex justify-content-center'>{invoice['invoice_number']}</div></td>
                                <td><div className='d-flex justify-content-center'>{invoice['seller']}</div></td>
								<td><div className='d-flex justify-content-center'>{invoice['buyer']}</div></td>
                                <td><div className='d-flex justify-content-center'>{new Date(invoice['verified_at']).toLocaleDateString('vi-VN')}</div></td>
                                <td><div className='d-flex justify-content-center'>{invoice['status'] ? <FaCircleCheck color="green" size={20}  /> : <BsFillXCircleFill color="red" size={20}/> }</div></td>
                            </tr>
                        })
                    }
                </tbody>
            </table>
            <nav aria-label="Page navigation example">
                <ul className="pagination">
                    <li className="page-item"><button className="page-link" onClick={() => {
                        if (page > 1) {
                            setPage(page => page - 1)
                        }
                    }}>Previous</button></li>
                    {renderPaginateNav()}
                    <li className="page-item"><button className="page-link" onClick={() => {
                        if (page <  pageTotal) {
                            setPage(page => page + 1)
                        }
                    }}>Next</button></li>
                </ul>
            </nav>
        </div>
    </div>)
}